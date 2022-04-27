import csv
import os
import sys

class Time:
    def __init__(self, jena_file, jenaclone_file, leapfrog_file, query, jena_time, jenaclone_time, leapfrog_time, jena_result_count, jenaclone_result_count, leapfrog_result_count, dictionary_usage):
        self.jena_file = jena_file
        self.jenaclone_file = jenaclone_file
        self.leapfrog_file = leapfrog_file
        self.query = query
        self.__jena_time = jena_time
        self.__jenaclone_time = jenaclone_time
        self.__leapfrog_time = leapfrog_time
        self.__jena_rs_count = jena_result_count
        self.__jenaclone_rs_count = jenaclone_result_count
        self.__leapfrog_rs_count = leapfrog_result_count
        self.__bgp_size = self.__compute_bgp_size()
        self.__var_count = len(self.__unique_variables())
        self.__dictionary_usage = dictionary_usage # List of boolean values: True means the dictionary returned positive, False otherwise. Length of list is amount of times the dictionary was used.

    def __compute_bgp_size(self):
        count = 0
        uri_dot_count = self.query.count('http') * 2

        for c in self.query:
            if (c == '.'):
                count += 1

        return (count + 1) - uri_dot_count

    def __unique_variables(self):
        vars = list()

        for ci in range(len(self.query)):
            if (self.query[ci] == '?'):
                var_name = ''

                while (self.query[ci] != ' '):
                    var_name += self.query[ci]
                    ci += 1

                vars.append(var_name)

        return list(set(vars))

    def get_jena_file(self):
        return self.jena_file

    def get_jenaclone_file(self):
        return self.jenaclone_file

    def get_leapfrog_file(self):
        return self.leapfrog_file

    def get_query(self):
        return self.query

    def get_jena_time(self):
        return self.__jena_time

    def get_jenaclone_time(self):
        return self.__jenaclone_time

    def get_leapfrog_time(self):
        return self.__leapfrog_time

    def has_optional(self):
        return 'OPTIONAL' in self.query

    def jena_resultset_size(self):
        return self.__jena_rs_count

    def jenaclone_resultset_size(self):
        return self.__jenaclone_rs_count

    def leapfrog_resultset_size(self):
        return self.__leapfrog_rs_count

    def bgp_size(self):
        return self.__bgp_size

    def get_variable_count(self):
        return self.__var_count

    def dictionary_usage(self):
        return self.__dictionary_usage

    def add_dictionary_usage(self, val):
        self.__dictionary_usage.append(val)

# Returns list of folder in directory.
def dir_folders(dir):
    dir_elements = os.listdir(dir)
    return list(filter(lambda elem: not elem.__contains__('.'), dir_elements))

# Checks if directory has files 'jena' and 'jenaclone'.
def has_results(dir):
    files = os.listdir(dir)
    return 'jena.csv' in files and 'jenaclone.csv' in files and 'leapfrog.csv' in files

# Creates a list of queries given a file.
def query_list(file):
    with open(file, 'r') as file:
        queries = list()
        lines = file.readlines()

        for line in lines:
            queries.append(line.rstrip('\n'))

        return queries

# List of .txt files of queries.
def query_files(dir):
    files = os.listdir(dir)
    return list(filter(lambda elem: elem.endswith('.txt'), files))

# List of benchmark times and resultset sizes for a given file.
def benchmark_times(file):
    with open(file, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter = ',')
        first = True
        times = list()

        for row in csv_reader:
            if (first):
                first = False

            elif(row[2] == 'timeout'):
                times.append((0, -1))

            else:
                time = int(row[2]) / 1000000     # milliseconds
                times.append((int(row[1]), time))

        return times

# Path to benchmark result file.
def benchmark_file(base, folder, query_file, result_file):
    return base + folder + '/' + query_file.rstrip('.txt') + '/' + result_file
