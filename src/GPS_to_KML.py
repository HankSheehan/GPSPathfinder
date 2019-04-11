import argparse
import pynmea2
import simplekml
from pprint import pprint
import re


def gps_to_kml(gps_file_path):
    # Read in and parse the GPS file
    with open(gps_file_path, 'r') as file:
        positions = []
        for position in file:
            try:
                positions.append(pynmea2.parse(position, check=False))
            except:
                continue

    # Write data to a KML object
    kml = simplekml.Kml()

    path = kml.newlinestring(
        name="Example",
        description="Path for 2019_03_19",
        coords=[(position.longitude, position.latitude) for position in positions]
    )

    path.style.linestyle.color = 'Af00ffff'
    path.style.linestyle.width = 6
    path.style.polystyle.color('7f00ff00'

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
