from pykml import parser
import os

DATA_FILES_DIR = 'data'
KML_FILES_DIR = 'kml'

def main():
	data_files = load_files(DATA_FILES_DIR)
	kml_files = load_files(KML_FILES_DIR)

def load_files(dir):
	for file in os.listdir(os.fsencode(dir)):
	     filename = os.fsdecode(file)
	     if filename.endswith(".txt"):
	     	return load_gps_txt(file)
	     elif filename.endswith(".kml"):
	     	return load_gps_kml(file)

def load_gps_kml():
	return

def load_gps_txt():
	return

main()
	