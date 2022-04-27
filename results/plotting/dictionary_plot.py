import matplotlib.pyplot as plt
import numpy as np
import sys, os

p = os.path.abspath('..')
sys.path.insert(1, p)

from dictionary_check import *
from parser import *

QUERY_BASE_DIR = '../../benchmark/queries/'
RESULTS_BASE_DIR = '../'
BENCHMARK_OUTPUT = '../benchmark_output.txt'

def get_query_name(path):
    direction_count = len(path.split('/'))
    query_name = path.split('/')[direction_count - 2]
    return query_name

def boxplot(times):
    plt.figure(figsize = (5, 7))
    plt.xlabel("Jenaclone", fontsize = 18)
    plt.ylabel("Dictionary frequency", fontsize = 18)
    plt.boxplot([count_dict_usage(times, True), count_dict_usage(times, False)], labels = ["Positive", "Negative"])
    plt.savefig("charts/dictionary_usage.pdf", format = "pdf")
    plt.close('all')

def count_dict_usage(times, type):
    counts = list()

    for time in times:
        count = len(list(filter(lambda d: d == type, time.dictionary_usage())))
        counts.append(count)

    return counts

if __name__ == "__main__":
    folders = list()
    times = list()
    dict_lines = list()

    for i in range(len(sys.argv) - 1):
        folders.append(sys.argv[i + 1])

    for folder in folders:
        files = query_files(QUERY_BASE_DIR + folder)

        for query_file in files:
            jenaclone_file = benchmark_file(RESULTS_BASE_DIR, folder, query_file, 'jenaclone.csv')
            queries = query_list(QUERY_BASE_DIR + folder + '/' + query_file)
            jenaclone_times = benchmark_times(jenaclone_file)

            for i in range(len(queries)):
                times.append(Time(None, jenaclone_file, None, queries[i], None, jenaclone_times[i][1], None, None, jenaclone_times[i][0], None, []))

    i = 0
    limit = 100000000

    with open(BENCHMARK_OUTPUT, "r") as dict_output:
        for line in dict_output:
            dict_lines.append(line)
            i += 1

            if (i == limit):
                break

    check_for_dictionary_use(times, dict_lines)
    times.sort(key = lambda time: time.get_jenaclone_time())
    boxplot(times)
