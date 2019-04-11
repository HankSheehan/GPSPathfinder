import argparse
import pynmea2
import simplekml
from pprint import pprint
import re


FILTER_GPGGA = '\$GPGGA.*'
FILTER_GPRMC = '\$GPRMC.*'

def gps_to_kml(gps_file_path):
    with open(gps_file_path, 'r') as file:
        lines = []
        for line in file:
            if re.match(f'{FILTER_GPRMC}|{FILTER_GPGGA}', line):
                try:
                    lines.append(pynmea2.parse(line, check=False))
                except:
                    continue

        pprint(lines)

    return ''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('gps_file_path')
    parser.add_argument('kml_file_path')
    args = parser.parse_args()
    gps_file_path = args.gps_file_path
    kml_file_path = args.kml_file_path

    with open(kml_file_path, 'w') as kml_fp:
        kml_fp.write(gps_to_kml(gps_file_path))


if __name__ == '__main__':
    main()
