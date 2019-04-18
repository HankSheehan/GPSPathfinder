# Python Standard Libraries
import argparse
from pprint import pprint
import re

# Third Party Libraries
import pynmea2
import simplekml
from haversine import haversine

LINESTYLE_COLOR = 'Af00ffff'
LINESTYLE_WIDTH = 6
POLYSTYLE_COLOR = '7f00ff00'

VALID_GPS_LINE_REGEX = '^\$GPRMC,\d+\.\d+,A,\d+.\d+,N,\d+.\d+,W,\d+.\d+,\d+.\d+,\d+(,[^,\n]*){3}$'

KNOT_TO_MPH = 1.15078 # 1 knot = this many mph
ACCELERATION_THRESHOLD = 15 # mph
DECELERATION_THRESHOLD = 15 # mph
PROJECTED_DISTANCE_THRESHOLD = 20 # miles



def write_kml_file(positions, kml_file_path, sanatized_points=[]):
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

    # Add red pins for all sanatized points
    for position in sanatized_points:
        pnt = kml.newpoint(
            name="Sanatized point",
            coords=[get_coordinate_tuple(position)]
        )
        pnt.style.labelstyle.color = simplekml.Color.red

    with open(kml_file_path, 'w') as kml_fp:
        kml_fp.write(kml.kml())


def load_gps_file(gps_file_path):
    """
    Read in and parse the GPS file. Lines that cannot be parsed are ignored.
    """
    with open(gps_file_path, 'r') as file:
        positions = []
        for position in file:
            if re.match(VALID_GPS_LINE_REGEX, position):
                try:
                    positions.append(pynmea2.parse(position, check=False))
                except:
                    continue

    return positions


def sanitize_data(positions):
    """
    Cleans bad data points
    """

    print(f'{len(positions)} positions before sanitization')
    bad_points = []

    index = 0
    while index < len(positions):
        current_position = positions[index]
        last_position = positions[index-1]

        # if not acceleration_is_valid(current_position, last_position):
        #     bad_points.append(current_position)
        #     positions.pop(index)
        if not position_within_projection(current_position, last_position):
            bad_points.append(current_position)
            positions.pop(index)
        else:
            index += 1



    print(f'{len(positions)} positions after sanitization')
    return positions, bad_points


def acceleration_is_valid(current_position, last_position):
    current_speed = get_speed(current_position)
    last_speed = get_speed(last_position)
    speed_difference_per_second = abs(current_speed - last_speed)/(current_position.datetime - last_position.datetime).total_seconds()
    # Accelerating
    if current_speed > last_speed:
        return speed_difference_per_second < ACCELERATION_THRESHOLD
    # Decelerating
    else:
        return speed_difference_per_second < DECELERATION_THRESHOLD


def position_within_projection(current_position, last_position):
    last_speed = get_speed(last_position)
    hours_since_last_position = (current_position.datetime - last_position.datetime).total_seconds() / 3600
    distance_from_last_position = get_distance(current_position, last_position)
    projected_distance = last_speed * hours_since_last_position
    print(f'projected distance: {projected_distance}')
    print(f'hours since last: {hours_since_last_position}')
    print(f'last speed: {last_speed}')
    print(f'distanace from last: {distance_from_last_position}\n')
    return distance_from_last_position < projected_distance + PROJECTED_DISTANCE_THRESHOLD


def get_speed(position):
    """
    Returns the speed at this position in miles per hour.
    """
    if isinstance(position, pynmea2.types.talker.RMC):
        return position.spd_over_grnd * KNOT_TO_MPH

    return None


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
    gps_data, sanatized_points = sanitize_data(gps_data)
    write_kml_file(gps_data, kml_file_path, sanatized_points)


if __name__ == '__main__':
    main()
