from vocaloidfile import VprConverter
import argparse

# args_parser = argparse.ArgumentParser()
# args_parser.add_argument('vprFile', required=True)
# args_parser.add_argument('csvFile', required=True)
# args_parser.add_argument('--out', required=False)
# args = args_parser.parse_args()

converter = VprConverter()
converter.set_vprsrc("test/test.vpr")
track = converter.add_default_track()
part = converter.add_default_part(track)

converter.set_csvsrc("test/pitch.txt")
converter.add_pitch_to_part(part)
converter.set_csvsrc("test/intensity.txt")
converter.add_intensity_to_part(part, 30, 80)

converter.save_vpr()