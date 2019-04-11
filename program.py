# import os
# import simplekml

# DATA_FILES_DIR = 'data'

# def main():
#     data_files = load_files(DATA_FILES_DIR)

# def load_files(file_dir):
#     _, _, files = next(os.walk(file_dir))
#     files = list(filter(lambda file: file.lower().endswith('.txt'), files))
#     files = [os.path.join(file_dir, file) for file in files]

#     return files

#     # return gps_files

# def load_gps_data(file):
#     with open(file, 'r') as file:
#         return [ line for line in file ]

# main()
#     