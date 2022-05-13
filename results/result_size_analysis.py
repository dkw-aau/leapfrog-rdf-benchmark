from parser import *
from analysis import *
import os
import sys

OUT_FILE = "result_sizes.txt"

def print_intermediate_sizes(time, dataset):
    with open('query.txt', 'w') as file:
        file.write(time.get_query().replace("(COUNT(*) AS ?count)", "*"))

    os.system('java -jar JenaQueryTool.jar --loc ' + dataset + ' --query query.txt query intermediate >> result_sizes/' + time.get_jena_file().split('/')[2] + '-' + OUT_FILE)
    os.system('rm query.txt')

    with open('result_sizes/' + time.get_jena_file().split('/')[2] + '-' + OUT_FILE, 'a') as file:
        file.write('Jenaclone\t\tJena\t\tLeapfrog\n')
        file.write(str(time.get_jenaclone_time()) + '\t\t' + str(time.get_jena_time()) + '\t\t' + str(time.get_leapfrog_time()) + '\n')
        file.write(time.get_jena_file()[0:time.get_jena_file().rfind('/')] + "\n\n")

def analyze_sizes(file):
    with open(file, "r") as f:
        output = "Analysis\n\n"
        is_query = False
        is_plan = False
        results = None
        tp_sum = 0

        for line in f:
            if (is_query):
                is_query = False
                output += line + "\n\n"

            elif (is_plan):
                output += line

                if ("slice" in line):
                    results = int(line[line.find('(') + 1:line.find(')')])

                elif ("triple" in line):
                    tp_sum += int(line[line.find('(') + 1:line.find(')')])

                elif ("./" in line):
                    is_plan = False
                    output += "\nDifference (sum of triple pattern solutions and result set size): " + str(tp_sum - results) + "\n\n"
                    results = None
                    tp_sum = 0

            elif (line == "Query"):
                is_query = True
                output += line + "\n"

            elif ("Intermediate" in line):
                is_plan = True
                output += line + "\n"

    os.system('rm ' + file)

    with open(file, 'w') as f:
        f.write(output)

if __name__ == "__main__":
    folders = list()

    if (len(sys.argv) < 3):
        raise 'First argument must be path to database files and the remaining arguments must be result folders'

    for i in range(len(sys.argv) - 2):
        folders.append(sys.argv[i + 2])

    folders_exist_check(folders)

    dataset = sys.argv[1]
    os.system('mkdir result_sizes')

    for folder in folders:
        files = query_files(QUERY_BASE_DIR + folder)

        for query_file in files:
            jena_file = benchmark_file(RESULTS_BASE_DIR, folder, query_file, 'jena.csv')
            jenaclone_file = benchmark_file(RESULTS_BASE_DIR, folder, query_file, 'jenaclone.csv')
            leapfrog_file = benchmark_file(RESULTS_BASE_DIR, folder, query_file, 'leapfrog.csv')

            queries = query_list(QUERY_BASE_DIR + folder + '/' + query_file)
            jena_times = benchmark_times(jena_file)
            jenaclone_times = benchmark_times(jenaclone_file)
            leapfrog_times = benchmark_times(leapfrog_file)

            for i in range(3):
                time = Time(jena_file, jenaclone_file, leapfrog_file, queries[i], jena_times[i][1], jenaclone_times[i][1], leapfrog_times[i][1], jena_times[i][0], jenaclone_times[i][0], leapfrog_times[i][0], [])
                print_intermediate_sizes(time, dataset)

            analyze_sizes('result_sizes/' + jena_file.split('/')[2] + '-' + OUT_FILE)
