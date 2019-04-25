import argparse
import simplekml

import GPS_to_KML as gps_utils

STOP_MERGE_THRESHOLD = .05
STOP_MARKER_TYPE = 0
LEFT_TURN_MARKER_TYPE = 1
RIGHT_TURN_MARKER_TYPE = 2


def sanitize_markers(stop_positions, left_turn_positions, right_turn_positions):
    # Add labels to the positions (to keep track of them)
    for position in stop_positions:
        position.marker_type = STOP_MARKER_TYPE
    for position in left_turn_positions:
        position.marker_type = LEFT_TURN_MARKER_TYPE
    for position in right_turn_positions:
        position.marker_type = RIGHT_TURN_MARKER_TYPE


    # TODO: Actually sanatize these markers


    return stop_positions, left_turn_positions, right_turn_positions

def detect_stops(positions):
    """
    Given a list of GPS positions from a single path, return a list of positions of stops.
    """
    # Detect stops
    stop_positions = []
    for position in positions:
        if gps_utils.get_speed(position) < 15:
            stop_positions.append(position)

    return stop_positions


def detect_left_turns(positions):
    """
    Given a list of GPS positions from a single path, return a list of positions of left turns.
    """
    # TODO: Actually detect left turn
    return []


def detect_right_turns(positions):
    """
    Given a list of GPS positions from a single path, return a list of positions of right turns.
    """
    # TODO: Actually detect right turn
    return []


def gps_to_cost_map(gps_file_paths):
    """
    Given a list of gps_file_paths, produce a map of stops, right turns, left turns, and the paths taken.
        All this data should be agglomerated so there are no doubles in the map.
    """
    total_positions = []
    stop_positions = []
    left_turn_positions = []
    right_turn_positions = []

    for file in gps_file_paths:
        # Load and sanatize data
        positions = gps_utils.load_gps_file(file)
        positions = gps_utils.sanitize_data(positions)

        # Detect the stops and turns
        detected_stop = detect_stops(positions)
        detected_left_turn = detect_left_turns(positions)
        detected_right_turn = detect_right_turns(positions)

        # Sanatize the markers
        detected_stop, detected_left_turn, detected_right_turn = sanitize_markers(detected_stop, detected_left_turn, detected_right_turn)

        stop_positions += detected_stop
        left_turn_positions += detected_left_turn
        right_turn_positions += detected_right_turn
        total_positions += positions

    return positions, stop_positions, left_turn_positions, right_turn_positions


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('gps_file_paths', nargs='+')
    parser.add_argument('kml_file_path')
    args = parser.parse_args()
    gps_file_paths = args.gps_file_paths
    kml_file_path = args.kml_file_path

    positions, stops, left_turns, right_turns = gps_to_cost_map(gps_file_paths)

    gps_utils.write_kml_file(kml_file_path, positions, stops, left_turns, right_turns)


if __name__ == '__main__':
    main()
