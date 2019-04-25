# Python Standard Libraries
import argparse
from pprint import pprint
import re

# Third Party Libraries
import pynmea2
import simplekml
from haversine import haversine

PATH_LINESTYLE_COLOR = 'Af00ffff'
PATH_LINESTYLE_WIDTH = 6
PATH_POLYSTYLE_COLOR = '7f00ff00'

POINT_LABELSTYLE_COLOR = simplekml.Color.white
STOP_ICONSTYLE_COLOR = simplekml.Color.yellow
LEFT_TURN_ICONSTYLE_COLOR = simplekml.Color.red
RIGHT_TURN_ICONSTYLE_COLOR = simplekml.Color.green

VALID_GPS_LINE_REGEX = '^\$GPRMC,\d+\.\d+,A,\d+.\d+,N,\d+.\d+,W,\d+.\d+,\d+.\d+,\d+(,[^,\n]*){3}$'

KNOT_TO_MPH = 1.15078 # 1 knot = this many mph
ACCELERATION_THRESHOLD = 15 # mph
DECELERATION_THRESHOLD = 15 # mph
PROJECTED_DISTANCE_THRESHOLD = 1 # mph



def write_kml_file( kml_file_path,
                    positions,
                    stop_positions=[],
                    left_turn_positions=[],
                    right_turn_positions=[]
                    ):
    """
    Takes in a list of GPS positions and write them to a kml file
    """
    kml = simplekml.Kml()

    if positions:

        # Add a line for the path taken
        path = kml.newlinestring(
            name="Path",
            description="Path",
            altitudemode="relativeToGround",
            extrude=1,
            coords=[get_coordinate_and_speed_tuple(position) for position in positions]
        )

        path.style.linestyle.color = PATH_LINESTYLE_COLOR
        path.style.linestyle.width = PATH_LINESTYLE_WIDTH
        path.style.polystyle.color = PATH_POLYSTYLE_COLOR

    # Add markers for stops
    for position in stop_positions:
        stop_marker = kml.newpoint(name="stop", description="Detected stop.", coords=[get_coordinate_tuple(position)])
        stop_marker.style.labelstyle.color = POINT_LABELSTYLE_COLOR
        stop_marker.style.iconstyle.color = STOP_ICONSTYLE_COLOR

    # Add markers for left turns
    for position in left_turn_positions:
        left_turn_marker = kml.newpoint(name="left turn", description="Detected left turn.", coords=[get_coordinate_tuple(position)])
        left_turn_marker.style.labelstyle.color = POINT_LABELSTYLE_COLOR
        left_turn_marker.style.iconstyle.color = LEFT_TURN_ICONSTYLE_COLOR

    # Add markers for right turns
    for position in right_turn_positions:
        right_turn_marker = kml.newpoint(name="right turn", description="Detected right turn.", coords=[get_coordinate_tuple(position)])
        right_turn_marker.style.labelstyle.color = POINT_LABELSTYLE_COLOR
        right_turn_marker.style.iconstyle.color = RIGHT_TURN_ICONSTYLE_COLOR

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


def get_coordinate_and_speed_tuple(position, lat_first=False):
    """
    Returns the longitude and latitude of this position as a tuple.
    If lat_first is True, the order will be reversed.
    """
    if lat_first:
        return (position.latitude, position.longitude, get_speed(position))
    else:
        return (position.longitude, position.latitude, get_speed(position))


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
