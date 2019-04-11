import argparse
import pynmea2
import simplekml
from pprint import pprint
import re


def gps_to_kml(gps_file_path):
    # Read in and parse the GPS file
    with open(gps_file_path, 'r') as file:
        lines = []
        for line in file:
            try:
                lines.append(pynmea2.parse(line, check=False))
            except:
                continue

    # Write data to a KML object
    kml = simplekml.Kml()
    coords=[(line.longitude, line.latitude) for line in lines]
    kml.newlinestring(name="Example", description="Path for 2019_03_19", coords=coords)


    return kml.kml()


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
