import argparse
import simplekml


def gps_to_cost_map(gps_file):
    return ''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('gps_file_paths', nargs='+')
    parser.add_argument('kml_file_path')
    args = parser.parse_args()
    gps_file_paths = args.gps_file_paths
    kml_file_path = args.kml_file_path

    with open(kml_file_path, 'w') as kml_fp:
        kml_fp.write(gps_to_cost_map(gps_file_paths))


if __name__ == '__main__':
    main()
