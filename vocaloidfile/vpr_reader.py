from pathlib import Path
import math
import json
import zipfile
import csv

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
        with zipfile.ZipFile(vprpath, 'r') as f:
            self.seq_data_raw = f.read(SEQ_PATH)
            self.seq_data = json.loads(self.seq_data_raw)
        return self.seq_data

    def set_csvsrc(self, csvpath):
        with open(csvpath, 'r', newline='', encoding="utf-8") as f:
            self.csv_data = list(csv.reader(f, delimiter=' '))
        return self.csv_data

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


    def add_pitch_to_part(self, part, time_col_name="Time_s", pitch_col_name="F0_Hz", start_offset=0):
        header = self.csv_data[0]
        try:
            time_col_idx = header.index(time_col_name)
            pitch_col_idx = header.index(pitch_col_name)
        except ValueError:
            return
        
        time = []
        pitch = []
        notes = []
        note_start = None
        for row in self.csv_data[1:]:
            time_value = float(row[time_col_idx])
            try:
                pitch_value = float(row[pitch_col_idx])
                if note_start == None:
                    note_start = time_value
            except ValueError:
                pitch_value = None
                if note_start != None:
                    notes.append([note_start, time_value])
                    note_start = None 
            time.append(time_value)
            pitch.append(pitch_value)

        min_pitch = min(p for p in pitch if p is not None)
        max_pitch = max(p for p in pitch if p is not None)
        mid_pitch = min_pitch * pow(2, get_semitone(min_pitch, max_pitch) / (12 * 2)) 
        pitch_range = get_semitone(mid_pitch, max_pitch)
        pbs = math.ceil(pitch_range)

        # check whether controller is already being in a part
        # pbs := [0, 24]
        # pitch bend := [-8192, 8191]
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

        # add control points
        self.add_controlpoint(controller_pbs, 0, min(pbs, 24))
        for idx in range(len(time)):
            pos = int(time[idx] * 1000)
            pos += start_offset
            if pitch[idx] == None:
                val = 0
            else:
                val = get_semitone(mid_pitch, pitch[idx]) / pbs * 8192
                val = max(-8192, min(int(val), 8191))
            self.add_controlpoint(controller_pb, pos, val)

        # add notes
        for start, end in notes:
            note = self.add_default_note(part)
            note["pos"] = int(start * 1000 + start_offset)
            note["duration"] = int((end - start) * 1000)

    def add_intensity_to_part(self, part, min_value, max_value, time_col_name="Time_s", intensity_col_name="Intensity_dB", start_offset=0):
        header = self.csv_data[0]
        try:
            time_col_idx = header.index(time_col_name)
            intensity_col_idx = header.index(intensity_col_name)
        except ValueError:
            return
        
        time = []
        intensity = []
        for row in self.csv_data[1:]:
            intensity_value = float(row[intensity_col_idx])
            time_value = float(row[time_col_idx])
            time.append(time_value)
            intensity.append(intensity_value)
        min_intensity, max_intensity = min(intensity), max(intensity)
        intensity_range = get_dB(min_intensity, max_intensity)

        # dyn := [0, 127]

        controller_dyn = None
        for controller in part["controllers"]:
            if controller["name"] == ControllerName.DYN:
                controller_dyn = controller
        if controller_dyn == None:
            controller_dyn = self.add_default_controller(part, ControllerName.DYN)

        for idx in range(len(time)):
            pos = int(time[idx] * 1000)
            pos += start_offset
            val = get_dB(min_intensity, intensity[idx]) / intensity_range
            val = (max_value - min_value) * val + min_value
            val = max(0, min(int(val), 127))
            self.add_controlpoint(controller_dyn, pos, val)

    def save_vpr(self):
        with zipfile.ZipFile(self.vprpath, 'w') as f:
            f.writestr(SEQ_PATH, json.dumps(self.seq_data))