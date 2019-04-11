import argparse
import pynmea2
import simplekml
from haversine import haversine
from pprint import pprint


LINESTYLE_COLOR = 'Af00ffff'
LINESTYLE_WIDTH = 6
POLYSTYLE_COLOR = '7f00ff00'

KNOT_TO_MPH = 1.15078 # 1 knot = this many mph
DISTANCE_THRESHOLD = 3000 # miles


def write_kml_file(positions, kml_file_path):
    """
    Takes in a list of GPS positions and write them to a kml file
    """
    kml = simplekml.Kml()

    path = kml.newlinestring(
        name="Example",
        description="Path for 2019_03_19",
        coords=[get_coordinate_tuple(position) for position in positions]
    )

    path.style.linestyle.color = LINESTYLE_COLOR
    path.style.linestyle.width = LINESTYLE_WIDTH
    path.style.polystyle.color = POLYSTYLE_COLOR

    with open(kml_file_path, 'w') as kml_fp:
        kml_fp.write(kml.kml())


def load_gps_file(gps_file_path):
    """
    Read in and parse the GPS file. Lines that cannot be parsed are ignored.
    """
    with open(gps_file_path, 'r') as file:
        positions = []
        for position in file:
            try:
                positions.append(pynmea2.parse(position, check=False))
            except:
                continue

        print(get_distance(positions[0], positions[1]))

    return positions


def sanitize_data(positions):
    """
    Cleans bad data points
    """
    return positions


def get_speed(position):
    """
    Returns the speed at this position in miles per hour.
    """
    return position.spd_over_grnd * KNOT_TO_MPH


def get_coordinate_tuple(position, lat_first=False):
    """
    Returns the longitude and latitude of this position as a tuple.
    If lat_first is True, the order will be reversed.
    """
    if lat_first:
        return (position.latitude, position.longitude)
    else:
        return (position.longitude, position.latitude)


def get_distance(position1, position2):
    """
    Returns haversine distance between two positions in miles.
    """
    return haversine(get_coordinate_tuple(position1, lat_first=True), get_coordinate_tuple(position2, lat_first=True), unit='mi')


def get_args():
    """
    Initializes argparse and returns desired arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('gps_file_path')
    parser.add_argument('kml_file_path')
    args = parser.parse_args()
    return args.gps_file_path, args.kml_file_path


def main():
    gps_file_path, kml_file_path = get_args()
    gps_data = load_gps_file(gps_file_path)
    gps_data = sanitize_data(gps_data)
    write_kml_file(gps_data, kml_file_path)


if __name__ == '__main__':
    main()
