from vocaloidfile import VprConverter
import argparse

args_parser = argparse.ArgumentParser()
args_parser.add_argument('vprFile')
args_parser.add_argument('csvFile', nargs="+")
args_parser.add_argument('--out')
args = args_parser.parse_args()

converter = VprConverter()
converter.set_vprsrc(args.vprFile)
track = converter.add_default_track()
part = converter.add_default_part(track)

for csvpath in args.csvFile:
    converter.set_csvsrc(csvpath)
    converter.add_pitch_to_part(part)
    converter.add_intensity_to_part(part, 30, 80)

converter.save_vpr()