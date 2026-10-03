#!/usr/bin/env python3

from vocaloidfile import VprConverter
import praat
import argparse

args_parser = argparse.ArgumentParser()
args_parser.add_argument('vprFile')
args_parser.add_argument('audioFile', nargs="+", help="Audio file(s) to analyze with praat")
args_parser.add_argument('--out', help="vpr file will modified. Omit this will modify input vpr file.")
args_parser.add_argument('--start-offset', type=int, default=0, help="Time of vpr part to start in milisecond")
args_parser.add_argument('--tone-offset', type=int, default=0, help="Tone offset in semitone")
args_parser.add_argument('--dyn-range', nargs=2, type=int, default=[20, 100], help="min and max of Dyn value", metavar=('MIN', 'MAX'))
args_parser.add_argument('--praat', help="Path of praat executable. Omit this will search PRAAT_PATH, PATH and default install locations.")
args_parser.add_argument('--pitch-floor', type=float, default=75, help="Pitch floor in Hz")
args_parser.add_argument('--pitch-ceiling', type=float, default=600, help="Pitch ceiling in Hz")
args_parser.add_argument('--time-step', type=float, default=0, help="Analysis time step in second. 0 means praat's automatic value")
args = args_parser.parse_args()

converter = VprConverter()
converter.set_vprsrc(args.vprFile)
track = converter.add_default_track()
part = converter.add_default_part(track)

for audiopath in args.audioFile:
    data = praat.extract(audiopath, praat_path=args.praat, time_step=args.time_step,
                         pitch_floor=args.pitch_floor, pitch_ceiling=args.pitch_ceiling)
    converter.set_analysis(data)
    converter.add_pitch_to_part(part, start_offset=args.start_offset, tone_offset=args.tone_offset)
    converter.add_intensity_to_part(part, args.dyn_range[0], args.dyn_range[1], start_offset=args.start_offset)

converter.save_vpr(vprpath=args.out)
