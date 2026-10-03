import bisect

TICKS_PER_QUARTER = 480

class TempoMap:
    """Converts between absolute time in seconds and vpr ticks using masterTrack.tempo"""
    def __init__(self, tempo_json):
        if tempo_json.get("global", {}).get("isEnabled"):
            events = [(0, tempo_json["global"]["value"])]
        else:
            events = sorted((e["pos"], e["value"]) for e in tempo_json["events"])
        if not events:
            events = [(0, 12000)]
        # tempo of the first event also applies before it
        if events[0][0] > 0:
            events.insert(0, (0, events[0][1]))

        # each segment: start tick, start second, bpm (value is bpm * 100)
        self.ticks = []
        self.secs = []
        self.bpms = []
        sec = 0.0
        for idx, (tick, value) in enumerate(events):
            if idx > 0:
                prev_tick, prev_bpm = self.ticks[-1], self.bpms[-1]
                sec += (tick - prev_tick) * 60 / (prev_bpm * TICKS_PER_QUARTER)
            self.ticks.append(tick)
            self.secs.append(sec)
            self.bpms.append(value / 100)

    def sec_to_tick(self, sec):
        idx = max(0, bisect.bisect_right(self.secs, sec) - 1)
        tick = self.ticks[idx] + (sec - self.secs[idx]) * self.bpms[idx] * TICKS_PER_QUARTER / 60
        return round(tick)

    def tick_to_sec(self, tick):
        idx = max(0, bisect.bisect_right(self.ticks, tick) - 1)
        return self.secs[idx] + (tick - self.ticks[idx]) * 60 / (self.bpms[idx] * TICKS_PER_QUARTER)
