from pathlib import Path
import math
import json
import zipfile

DIR = Path(__file__).resolve().parent

with open(DIR / "default_note.json", 'r', encoding="utf-8") as file:
    DEFAULT_NOTE_RAW = file.read()

with open(DIR / "default_controller.json", 'r', encoding="utf-8") as file:
    DEFAULT_CONTROLLER_RAW = file.read()

with open(DIR / "default_part.json", 'r', encoding="utf-8") as file:
    DEFAULT_PART_RAW = file.read()

with open(DIR / "default_track.json", 'r', encoding="utf-8") as file:
    DEFAULT_TRACK_RAW = file.read()

SEQ_PATH = "Project/sequence.json"
A3_NUM = 69

def get_semitone(freq1, freq2):
    return math.log2(freq2 / freq1) * 12

def get_dB(val1, val2):
    return math.log10(val2 / val1) * 10

class ControllerName:
    DYN = "dynamics"
    PB = "pitchBend"
    PBS = "pitchBendSens"

class VprConverter:
    def set_vprsrc(self, vprpath):
        self.vprpath = vprpath
        try:
            with zipfile.ZipFile(vprpath, 'r') as f:
                self.seq_data_raw = f.read(SEQ_PATH)
                self.seq_data = json.loads(self.seq_data_raw)
        except zipfile.BadZipFile as e:
            raise RuntimeError(f"Can not open {vprpath} as .vpr file") from e
        self.tuning_freq = self.seq_data["masterTrack"]["mainTuning"]
        return self.seq_data

    def set_analysis(self, data):
        """data: {"time": [...], "f0": [...], "intensity": [...]}, undefined values are nan"""
        self.notes = None
        self.intensity = None
        if "f0" in data:
            self.parse_pitch(data["time"], data["f0"])
        if "intensity" in data:
            self.parse_intensity(data["time"], data["intensity"])
        return data

    def parse_pitch(self, times, f0s):
        self.notes = []
        note_start = None
        for time_value, pitch_value in zip(times, f0s):
            if not math.isnan(pitch_value):
                if note_start == None:
                    note_start = time_value
                    time = []
                    pitch = []
                time.append(time_value)
                pitch.append(pitch_value)
            else:
                if note_start != None:
                    self._flush_note(note_start, time_value, time, pitch)
                    note_start = None 

        if note_start != None: 
            self._flush_note(note_start, max(times) + 1, time, pitch)

    def _flush_note(self, note_start, time_value, time, pitch):
        note = {}
        note["bound"] = (note_start, time_value)
        note["time"] = time
        note["pitch"] = pitch
        note["pitch_max"], note["pitch_min"] = max(pitch), min(pitch)
        note["pitch_mid"] = note["pitch_min"] * pow(2, get_semitone(note["pitch_min"], note["pitch_max"]) / (12 * 2)) 
        note["pbs"] = math.ceil(get_semitone(note["pitch_mid"], note["pitch_max"]))
        self.notes.append(note)



    def parse_intensity(self, times, intensities):
        time = []
        intensity = []
        for time_value, intensity_value in zip(times, intensities):
            if math.isnan(intensity_value):
                continue
            time.append(time_value)
            intensity.append(intensity_value)
        if not intensity:
            return
        min_intensity, max_intensity = min(intensity), max(intensity)

        self.intensity = {}
        self.intensity["time"] = time
        self.intensity["intensity"] = intensity
        self.intensity["intensity_max"], self.intensity["intensity_min"] = max_intensity, min_intensity
        self.intensity["intensity_range"] = max_intensity - min_intensity

    def add_default_track(self):
        new_track = json.loads(DEFAULT_TRACK_RAW)
        self.seq_data["tracks"].append(new_track)
        return new_track

    def add_default_part(self, track):
        new_part = json.loads(DEFAULT_PART_RAW)
        track["parts"].append(new_part)
        return new_part

    def add_default_note(self, part):
        new_note = json.loads(DEFAULT_NOTE_RAW)
        part["notes"].append(new_note)
        return new_note

    def add_default_controller(self, part, name):
        new_controller = json.loads(DEFAULT_CONTROLLER_RAW)
        new_controller["name"] = name
        part["controllers"].append(new_controller)
        return new_controller

    def add_controlpoint(self, controller, pos, value):
        controller["events"].append({"pos": pos, "value": value})


    def add_pitch_to_part(self, part, start_offset=0, tone_offset=0):
        if self.notes is None:
            return
        # check whether controller is already being in a part
        controller_pbs, controller_pb = None, None
        for controller in part["controllers"]:
            if controller["name"] == ControllerName.PB:
                controller_pb = controller
            elif controller["name"] == ControllerName.PBS:
                controller_pbs = controller
        if controller_pb == None:
            controller_pb = self.add_default_controller(part, ControllerName.PB)
        if controller_pbs == None:
            controller_pbs = self.add_default_controller(part, ControllerName.PBS)

        # add notes and control points in each note
        # pbs := [0, 24]
        # pitch bend := [-8192, 8191]
        for note in self.notes:
            startpos = int(note["bound"][0] * 1000) + start_offset
            endpos = int(note["bound"][1] * 1000) + start_offset

            self.add_controlpoint(controller_pbs, startpos, max(1, min(note["pbs"], 24)))
            for idx in range(len(note["time"])):
                pos = int(note["time"][idx] * 1000)
                pos += start_offset
                val = get_semitone(note["pitch_mid"], note["pitch"][idx]) / note["pbs"] * 8192
                val = max(-8192, min(int(val), 8191))
                self.add_controlpoint(controller_pb, pos, val)

            new_note = self.add_default_note(part)
            new_note["pos"], new_note["duration"] = startpos, endpos - startpos
            new_note["number"] = A3_NUM + round(get_semitone(self.tuning_freq, note["pitch_mid"])) + tone_offset

            if startpos < part["pos"]:
                part["pos"] = startpos
            if part["pos"] + part["duration"] < endpos:
                part["duration"] = endpos - part["pos"]


    def add_intensity_to_part(self, part, min_value, max_value, start_offset=0):
        if self.intensity is None:
            return
        if min_value > max_value:
            raise ValueError("min_value is bigger than max_value")

        # check controller is already being
        controller_dyn = None
        for controller in part["controllers"]:
            if controller["name"] == ControllerName.DYN:
                controller_dyn = controller
        if controller_dyn == None:
            controller_dyn = self.add_default_controller(part, ControllerName.DYN)

        # add control points
        # dyn := [0, 127]
        for idx in range(len(self.intensity["time"])):
            pos = int(self.intensity["time"][idx] * 1000)
            pos += start_offset
            val = (self.intensity["intensity"][idx] - self.intensity["intensity_min"]) / self.intensity["intensity_range"]
            val = (max_value - min_value) * val + min_value
            val = max(0, min(int(val), 127))
            self.add_controlpoint(controller_dyn, pos, val)

            if pos < part["pos"]:
                part["pos"] = pos
            if part["pos"] + part["duration"] < pos:
                part["duration"] = pos - part["pos"]

    def save_vpr(self, vprpath=None):
        if vprpath is None:
            vprpath = self.vprpath
        with zipfile.ZipFile(vprpath, 'w') as f:
            f.writestr(SEQ_PATH, json.dumps(self.seq_data))