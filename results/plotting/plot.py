# First argument is path to becnhmark results.
# Second argument is number of partitions of boxplot (1 means one boxplot of everything).

import os
import sys
import matplotlib.pyplot as plt
import numpy as np

TIMEOUT_VALUE = 1200000

def dir_folders(dir):
    dir_elements = os.listdir(dir)
    return list(filter(lambda elem: not elem.__contains__('.'), dir_elements))

def has_results(dir):
    files = os.listdir(dir)
    return 'jena.csv' in files and 'jenaclone.csv' in files and 'leapfrog.csv' in files

def read_result(file):
    with open(file, 'r') as read:
        lines = read.readlines()
        measurements = list()
        start = True

        for line in lines:
            if (start):
                start = False
                continue

            split_line = str(line).split(",")
            index = int(split_line[0])
            results = int(split_line[1])
            time = -1

            if (str(split_line[2]) != 'timeout\n'):
                time = int(split_line[2]) / 1000000    # Convert to milliseconds

            measurements.append([index, results, time])

        return measurements

def get_query_name(path):
    direction_count = len(path.split('/'))
    query_name = path.split('/')[direction_count - 2]
    jena_version = path.split('/')[direction_count - 1].split('.')[0]
    return query_name + '/' + jena_version

def result_files(dir):
    if (has_results(dir)):
        return list(dir + '/' + f for f in os.listdir(dir) if f.endswith('.csv'))

    folders = dir_folders(dir)
    files = list()

    for folder in folders:
        files = files + result_files(dir + '/' + folder)

    return files

def read_results(files):
    map = dict()

    for file in files:
        map[file] = read_result(file)

    return map

def benchmark_data(results):
    data = list()

    for result in results:
        if (result[2] != -1):
            data.append(result[2])

        else:
            data.append(TIMEOUT_VALUE)

    return data

def scale_fig_size(measurements, scale_rate):
    return (int(30 + measurements * scale_rate), 10)

def average_running_time(results_list):
    if (len(results_list) == 0):
        return 0

    sum = 0

    for result in results_list:
        sum += result[2]

    return sum / len(results_list)

def remove_outliers(results):
    keys = results.keys()
    outlier = 3

    for key in keys:
        new_results = list()
        avg = average_running_time(results[key])

        for i in range(len(results[key])):
            if (results[key][i][2] < avg * outlier):
                new_results.append(results[key][i])

        results[key] = new_results

# Assumes each Jena version are grouped in the list of result keys
def boxplot(results_map, jena_versions, out_dir, filename):
    keys = results_map.keys()
    charts_path = out_dir + '/' + filename
    y_label = 'Benchmark Time (milliseconds)'
    data_collection = list()
    labels = list()
    counter = 0

    for key in keys:
        labels.append(get_query_name(key))
        data_collection.append(benchmark_data(results_map[key]))
        counter += 1

        if (counter == jena_versions):
            plt.figure(figsize = ((jena_versions * 10) / 3, 7))
            plt.xlabel(labels[0].split('/')[0], fontsize = 18)
            plt.ylabel(y_label, fontsize = 18)
            plt.boxplot(data_collection, labels = list(map(lambda l: l.split('/')[1], labels)))
            plt.show()
            plt.savefig(charts_path + '_' + labels[0].split('/')[0] + '.pdf', format = 'pdf')
            plt.clf()

            labels = list()
            data_collection = list()
            counter = 0

# Counts number of queries running times that satisfy constraint
def query_times(constraint, results):
    queries = list()
    keys = results.keys()

    for key in keys:
        for i in range(len(results[key])):
            if (constraint(results[key][i][2])):
                queries.append(results[key][i][2])

    return queries

# Finds the slowest query running time
def slowest_time(results):
    slowest = 0
    keys = results.keys()

    for key in keys:
        for time in results[key]:
            if (time[2] > slowest):
                slowest = time[2]

    return slowest

# Constructs X-axis labels.
def x_labels(results, log, length_limit, unit, slowest_query_time):
    labels = list()
    prev = 1
    next = log
    labels.append('≤ ' + str(prev) + 'ms')

    for i in range(length_limit - 1):
        if (max(query_times(lambda time: time > prev and time <= next, results)) == slowest_query_time):
            labels.append(str(prev) + '-' + str(next) + 'ms')
            return labels

        labels.append(str(prev) + '-' + str(next) + 'ms')
        prev = next
        next = next * log

    labels.append('> ' + str(next) + 'ms')
    return labels

# Count of running times within each interval.
def running_times_count(results, log, length_limit):
    prev = 1
    next = log
    times = list()
    times.append(len(query_times(lambda time: time <= 1, results)))

    for i in range(length_limit - 1):
        filtered_times = query_times(lambda time: time > prev and time <= next, results)
        times.append(len(filtered_times))
        prev = next
        next = next * log

    times.append(len(query_times(lambda time: time > next, results)))
    return times

# Plots histogram of query running times
def run_times_histogram(results, out_dir):
    log = 10
    interval_count = 30
    slowest_query = slowest_time(results)
    labels = x_labels(results, log, interval_count, 'ms', slowest_query)
    times_count_jena = running_times_count({ key:value for (key, value) in results.items() if "jena.csv" in key }, log, len(labels) - 1)
    times_count_jenaclone = running_times_count({ key:value for (key, value) in results.items() if "jenaclone.csv" in key }, log, len(labels) - 1)
    times_count_leapfrog = running_times_count({ key:value for (key, value) in results.items() if "leapfrog.csv" in key }, log, len(labels) - 1)

    index = np.arange(len(labels))
    width = 0.2
    fig, ax = plt.subplots(figsize = (50, 10))
    ax.set_title('Running Times')
    ax.set_xlabel('Running time distribution')
    ax.set_ylabel('Number of queries')

    bar1 = ax.bar(index, times_count_jena, color = 'b', width = width, label = 'Jena')
    bar2 = ax.bar(index + width, times_count_jenaclone, color = 'g', width = width, label = 'Jenaclone')
    bar3 = ax.bar(index + 2 * width, times_count_leapfrog, color = 'r', width = width, label = 'Leapfrog')
    ax.legend()
    plt.xticks(index + width, labels)
    plt.show()
    plt.savefig(out_dir + '/running_times.pdf', format = 'pdf')

# Filters results map
def filter_results(results, predicate):
    filtered = dict()
    jena_results = None
    jenaclone_results = None
    leapfrog_results = None
    jena_key = None
    jenaclone_key = None
    leapfrog_key = None

    for key in results:
        if ("jena.csv" in key):
            jena_results = results[key]
            jena_key = key

        elif ("jenaclone.csv" in key):
            jenaclone_results = results[key]
            jenaclone_key = key

        elif ("leapfrog.csv" in key):
            leapfrog_results = results[key]
            leapfrog_key = key

        if (jena_key != None and jenaclone_key != None and leapfrog_key != None):
            filtered[jena_key] = list()
            filtered[jenaclone_key] = list()
            filtered[leapfrog_key] = list()

            for i in range(len(jena_results)):
                if (predicate(jena_results[i]) or predicate(jenaclone_results[i]) or predicate(leapfrog_results[i])):
                    filtered[jena_key].append(jena_results[i])
                    filtered[jenaclone_key].append(jenaclone_results[i])
                    filtered[leapfrog_key].append(leapfrog_results[i])

            jena_results = None
            jenaclone_results = None
            leapfrog_results = None
            jena_key = None
            jenaclone_key = None
            leapfrog_key = None

    return filtered

if __name__ == "__main__":
    path = '..'
    jena_versions = 3
    results = read_results(result_files(path))
    boxplot(results, jena_versions, 'charts', 'boxplot_all')
    boxplot(filter_results(results, lambda time: time[2] >= 100), jena_versions, 'charts', 'boxplot_slowest')
    run_times_histogram(results, 'charts')
