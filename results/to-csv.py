import csv
import os

# Returns list of folder in directory.
def dir_folders(dir):
    dir_elements = os.listdir(dir)
    return list(filter(lambda elem: not elem.__contains__('.'), dir_elements))

# Checks if directory has files 'jena' and 'jenaclone'.
def has_results(dir, result_file):
    files = os.listdir(dir)
    return result_file in files

# Finds result files and converts them to .csv files.
def to_csv(start_dir):
    if (not has_results(start_dir, 'jena') or not has_results(start_dir, 'jenaclone') or not has_results(start_dir, 'leapfrog')):
        folders = dir_folders(start_dir)

        for folder in folders:
            to_csv(start_dir + '/' + folder)
    else:
        convert(start_dir + '/jena')
        convert(start_dir + '/jenaclone')
        convert(start_dir + '/leapfrog')

# Writes .csv file from result input file.
def convert(file):
    with open(file, newline = '') as csv_read:
        csv_reader = csv.reader(csv_read, delimiter = ';')

        with open(file + '.csv', 'w', newline = '') as csv_write:
            csv_writer = csv.writer(csv_write, delimiter = ',')
            csv_writer.writerow(['index', 'results', 'average time (3)'])

            for row in csv_reader:
                csv_writer.writerow(row)

to_csv('.')
