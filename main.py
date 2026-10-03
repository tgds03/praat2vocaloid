#!/bin/python

from vocaloidfile import VprConverter
import argparse

args_parser = argparse.ArgumentParser()
args_parser.add_argument('vprFile')
args_parser.add_argument('csvFile', nargs="+")
args_parser.add_argument('--out', help="vpr file will modified. Omit this will modify input vpr file.")
args_parser.add_argument('--start-offset', type=int, default=0, help="Time of vpr part to start in milisecond")
args_parser.add_argument('--tone-offset', type=int, default=0, help="Tone offset in semitone")
args_parser.add_argument('--dyn-range', nargs=2, type=int, default=[20, 100], help="min and max of Dyn value", metavar=('MIN', 'MAX'))
args = args_parser.parse_args()

converter = VprConverter()
converter.set_vprsrc(args.vprFile)
track = converter.add_default_track()
part = converter.add_default_part(track)

for csvpath in args.csvFile:
    converter.set_csvsrc(csvpath)
    converter.add_pitch_to_part(part, start_offset=args.start_offset, tone_offset=args.tone_offset)
    converter.add_intensity_to_part(part, args.dyn_range[0], args.dyn_range[1], start_offset=args.start_offset)

converter.save_vpr(vprpath=args.out)