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
PROJECTED_DISTANCE_THRESHOLD = 1 # mph



def write_kml_file( kml_file_path,
                    positions,
                    stop_coordinates=[],
                    left_turn_coordinates=[],
                    right_turn_coordinates=[]
                    ):
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

    for coordinate in stop_coordinates:
        stop_marker = kml.newpoint(name="stops", description="Detected stop signs.", coords=[coordinate])

        stop_marker.style.linestyle.color = LINESTYLE_COLOR
        stop_marker.style.linestyle.width = LINESTYLE_WIDTH
        stop_marker.style.polystyle.color = POLYSTYLE_COLOR


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

    # Remove positions before trip begins
    positions = clean_trip_start(positions)

    # Clean up data based on it's acceleration
    index = 1
    while index < len(positions):
        current_position = positions[index]
        last_position = positions[index - 1]

        if not sequential_position_pair_is_valid(current_position, last_position):
            positions.pop(index)
        else:
            index += 1

        # print_some_info(current_position, last_position)


    # Remove positions after trip ends
    positions = clean_trip_end(positions)

    print(f'{len(positions)} positions after sanitization')
    return positions


def clean_trip_start(positions):
    while positions and get_speed(positions[0]) < 1:
        positions.pop(0)
    return positions


def clean_trip_end(positions):
    while positions and get_speed(positions[len(positions)-1]) < 1:
        positions.pop(len(positions)-1)
    return positions


def sequential_position_pair_is_valid(current_position, last_position):
    """
    Validates that two sequential positions are valid based on different
    constraints like timestasmps and acceleration
    """
    return (timestamp_is_valid(current_position, last_position)
        and acceleration_is_valid(current_position, last_position))


def timestamp_is_valid(current_position, last_position):
    """
    Returns True if the current position's timestamp comes after the previous
    position's timestamp
    """
    return current_position.timestamp > last_position.timestamp


def acceleration_is_valid(current_position, last_position):
    """
    Returns True if the current position's velocity has increased/decreased
    within a reasonable acceleration threshold
    """
    current_speed = get_speed(current_position)
    last_speed = get_speed(last_position)
    speed_difference_per_second = abs(current_speed - last_speed)/(current_position.datetime - last_position.datetime).total_seconds()
    # Accelerating
    if current_speed > last_speed:
        return speed_difference_per_second < ACCELERATION_THRESHOLD
    # Decelerating
    else:
        return speed_difference_per_second < DECELERATION_THRESHOLD


def print_some_info(current_position, last_position):
    last_speed = get_speed(last_position)
    distance_from_last_position = get_distance(current_position, last_position)
    print(f'last speed: {last_speed}')
    print(f'distanace from last: {distance_from_last_position}\n')


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
    gps_data = sanitize_data(gps_data)
    write_kml_file(kml_file_path, gps_data)


if __name__ == '__main__':
    main()
