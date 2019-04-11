import argparse
import simplekml


def gps_to_kml(gps_file_path):
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
