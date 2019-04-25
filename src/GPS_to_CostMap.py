# Python Standard Libraries
import argparse
import simplekml

import GPS_to_KML as gps_utils

# Third Party Libraries
import pynmea2

STOP_MERGE_THRESHOLD = .5 # miles
TURN_MERGE_THRESHOLD = .01 # miles
TURN_BEARING_DIFFERENCE_THRESHOLD = 15 # degrees
MARKER_MAX_SECONDS = 300 # seconds


def agglomerate_markers(marker_positions, threshold):
    """
    Takes in a list of marker positions and returns a list of lists of marker positions.
        The marker positions are grouped together if they are close together.
    """
    agglomerated_markers = []
    current_agglomeration = []
    for index, position in enumerate(marker_positions[1:]):
        last_position = marker_positions[index-1]
        if gps_utils.get_distance(position, last_position) < threshold:
            current_agglomeration.append(position)
        else:
            if current_agglomeration:
                agglomerated_markers.append(current_agglomeration)
            current_agglomeration = []

    return agglomerated_markers


def sanitize_markers(stop_positions, left_turn_positions, right_turn_positions, u_turn_positions):

    agglomerated_stop_positions = agglomerate_markers(stop_positions, STOP_MERGE_THRESHOLD)

    stop_positions = []
    for group in agglomerated_stop_positions:
        prune = False
        for position in left_turn_positions + right_turn_positions + u_turn_positions:
            if position in group:
                prune = True
                break
        if not prune:
            if (group[-1].datetime - group[0].datetime).total_seconds() > MARKER_MAX_SECONDS:
                continue
            stop_positions.append(group[0])

    return stop_positions, left_turn_positions, right_turn_positions, u_turn_positions


def get_metoid(positions):
    """
    Given a list of positions, get the metoid position.
    """
    centroid = lambda: None
    centroid.latitude = sum([position.latitude for position in positions]) / len(positions)
    centroid.longitude = sum([position.longitude for position in positions]) / len(positions)

    metoid = positions[0]
    best_distance = gps_utils.get_distance(positions[0], centroid)
    for position in positions:
        current_distance = gps_utils.get_distance(position, centroid)
        if current_distance < best_distance:
            metoid = position
            best_distance = current_distance
    return metoid


def detect_stops(positions):
    """
    Given a list of GPS positions from a single path, return a list of positions of stops.
    """
    # Detect stops
    stop_positions = []
    for position in positions:
        if gps_utils.get_speed(position) < 20:
            stop_positions.append(position)

    return stop_positions


def detect_turn(positions):
    """
    Given a list of GPS positions from a single path,
        return a list of right turn and a list of left turn positions.
    """
    # Detect slow downs
    slow_downs = []
    for position in positions:
        if gps_utils.get_speed(position) < 20:
            slow_downs.append(position)

    # Agglomerate slow down points that are close together
    left_turns = []
    right_turns = []
    u_turns = []
    agglomerated_slow_downs = agglomerate_markers(slow_downs, TURN_MERGE_THRESHOLD)

    for slow_down in agglomerated_slow_downs:
        if len(slow_down) <= 4:
            continue
        if (slow_down[-1].datetime - slow_down[0].datetime).total_seconds() > MARKER_MAX_SECONDS:
            continue

        # Get the bearings and add them to the turns list if the bear changes enough
        initial_bearing = gps_utils.get_bearing(slow_down[0], slow_down[1])
        final_bearing = gps_utils.get_bearing(slow_down[-2], slow_down[-1])
        bearing_difference = gps_utils.get_bearing_difference(initial_bearing, final_bearing)

        # TODO: handle U-turns (they sometimes freeak out)
        if abs(bearing_difference) > TURN_BEARING_DIFFERENCE_THRESHOLD:
            if abs(abs(bearing_difference)-180) < TURN_BEARING_DIFFERENCE_THRESHOLD:
                u_turns.append(get_metoid(slow_down))
            elif bearing_difference < 0:
                left_turns.append(get_metoid(slow_down))
            else:
                right_turns.append(get_metoid(slow_down))

    return left_turns, right_turns, u_turns


def gps_to_cost_map(gps_file_paths):
    """
    Given a list of gps_file_paths, produce a map of stops, right turns, left turns, and the paths taken.
        All this data should be agglomerated so there are no doubles in the map.
    """
    total_positions = []
    stop_positions = []
    left_turn_positions = []
    right_turn_positions = []
    u_turn_positions = []

    for file in gps_file_paths:
        # Load and sanatize data
        positions = gps_utils.load_gps_file(file)
        positions = gps_utils.sanitize_data(positions)

        # Detect the stops and turns
        detected_stop = detect_stops(positions)
        detected_left_turns, detected_right_turns, detected_u_turns = detect_turn(positions)

        # Sanatize the markers
        detected_stop, detected_left_turns, detected_right_turns, detected_u_turns = sanitize_markers(detected_stop, detected_left_turns, detected_right_turns, detected_u_turns)

        stop_positions += detected_stop
        left_turn_positions += detected_left_turns
        right_turn_positions += detected_right_turns
        u_turn_positions += detected_u_turns
        total_positions.append(positions)

    return total_positions, stop_positions, left_turn_positions, right_turn_positions, u_turn_positions


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('gps_file_paths', nargs='+')
    parser.add_argument('kml_file_path')
    args = parser.parse_args()
    gps_file_paths = args.gps_file_paths
    kml_file_path = args.kml_file_path

    positions, stops, left_turns, right_turns, u_turns = gps_to_cost_map(gps_file_paths)

    gps_utils.write_kml_file(kml_file_path, positions, stops, left_turns, right_turns, u_turns)


if __name__ == '__main__':
    main()
