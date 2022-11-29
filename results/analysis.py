# Pass names of folders in which query results are stored.

from parser import *
from dictionary_check import *
import sys
import math
import statistics

QUERY_BASE_DIR = '../benchmark/queries/'
RESULTS_BASE_DIR = './'
BENCHMARK_OUTPUT = 'benchmark_output.txt'
HEADER_IDENT = 8

# Checks for existence of given folders.
def folders_exist_check(folders):
    folders_queries = dir_folders(QUERY_BASE_DIR)
    folders_results = dir_folders(RESULTS_BASE_DIR)

    for folder in folders:
        if (folder not in folders_queries or folder not in folders_results):
            raise "No queries or results for passed folder names."

# Creates a header.
def header(header_txt):
    str = 100 * '#' + '\n'
    str += '#' + 98 * ' ' + '#\n'
    str += '#' + (49 - int(math.ceil(len(header_txt) / 2))) * ' ' + header_txt + (49 - int((len(header_txt) / 2))) * ' ' + '#\n'
    str += '#' + 98 * ' ' + '#\n'
    str+= 100 * '#' + '\n'
    return str

# Displays benchmark times for each query.
def display_times(times, predicate = None):
    print(header('QUERY TIMES WHERE JENACLONE IS AT LEAST 25% FASTER THAN JENA'))
    i = 1
    no_timeout = list(filter(lambda time: time.get_jena_time() != -1 and time.get_jenaclone_time() != -1, times))

    for time in no_timeout:
        improvement = float(time.get_jena_time() - time.get_jenaclone_time()) / time.get_jena_time()

        if (improvement >= 0.25):
            formatted_result = format_result(time.get_query(), [time.get_jena_time(), time.get_jenaclone_time()])
            print(str(i) + ".")
            print("Improvement: " + str(improvement))
            print('QUERY (' + time.get_jena_file().split('/')[-2] + ')' + HEADER_IDENT * '\t' + 'JENA' + HEADER_IDENT * '\t' + 'JENACLONE')
            print(formatted_result + '\n\n')
            i += 1

    print(header('QUERIES THAT ARE SLOWER THAN 1 SECOND FOR JENA OR JENACLONE'))
    i = 1

    for time in no_timeout:
        if (time.get_jena_time() >= 1000 or time.get_jenaclone_time() >= 1000):
            formatted_result = format_result(time.get_query(), [time.get_jena_time(), time.get_jenaclone_time()])
            print(str(i) + ".")
            print("Jena time - Jenaclone time: " + str(time.get_jena_time() - time.get_jenaclone_time()) + "ms")
            print('QUERY (' + time.get_jena_file().split('/')[-2] + ')' + HEADER_IDENT * '\t' + 'JENA' + HEADER_IDENT * '\t' + 'JENACLONE')
            print(formatted_result + '\n\n')
            i += 1

    print(header('QUERIES THAT USE DICTIONARY'))
    i = 1

    for time in times:
        if (len(time.dictionary_usage()) > 0):
            print(time.get_query() + '\n')
            print('Positive lookups: ' + str(len(list(filter(lambda val: val == True, time.dictionary_usage())))))
            print('Negative lookups: ' + str(len(list(filter(lambda val: val == False, time.dictionary_usage())))))
            print('Jenaclone time: ' + str(time.get_jenaclone_time()) + ' ms')
            print('Jena time: ' + str(time.get_jena_time()) + ' ms')
            print('Leapfrog time: ' + str(time.get_leapfrog_time()) + ' ms\n')

    print(header('STATS'))
    display_stats(times, predicate)

# Formats query.
def format_result(query, results):
    formatted = ''
    indentation = 0
    prev_char = ''
    first_line = True

    for c in query:
        if (c == '{'):
            indentation += 1
            formatted += c

            if (first_line):
                first_line = False

                for result in results:
                    formatted += (HEADER_IDENT - 2) * '\t' + str(result) + '\t'

            formatted += '\n' + indentation * 4 * ' '

        elif (c == '}'):
            indentation -= 1
            formatted += '\n' + indentation * 4 * ' '
            formatted += c

        elif (c == '.' and prev_char == ' '):
            formatted += '.\n'
            formatted += indentation * 4 * ' '

        else:
            formatted += c

        prev_char = c

    return formatted

# Formats statistic.
def format_stat(stat_title, jenaclone_stat, jena_stat, leapfrog_stat = None, allow_mod = True):
    width_factor = 6

    jenaclone_stat_mod = str(jenaclone_stat)
    jena_stat_mod = str(jena_stat)
    leapfrog_stat_mod = str(leapfrog_stat)

    if ('.' in jenaclone_stat_mod and allow_mod):
        jenaclone_stat_mod = jenaclone_stat_mod[:jenaclone_stat_mod.find('.') + 3]

    if ('.' in jena_stat_mod and allow_mod):
        jena_stat_mod = jena_stat_mod[:jena_stat_mod.find('.') + 3]

    if ('.' in leapfrog_stat_mod and allow_mod):
        leapfrog_stat_mod = leapfrog_stat_mod[:leapfrog_stat_mod.find('.') + 3]

    if (leapfrog_stat != None):
        width_factor = 2

    text = add_newlines(stat_title, 50)
    text += '\nJenaclone' + width_factor * '\t' + 'Jena'

    if (leapfrog_stat != None):
        text += width_factor * '\t' + 'Leapfrog'

    text += '\n' + jenaclone_stat_mod + width_factor * '\t' + jena_stat_mod

    if (leapfrog_stat != None):
        text += width_factor * '\t' + leapfrog_stat_mod

    return text

# Inserts newline when string is too long.
def add_newlines(str, len):
    split = ''
    counter = 0

    for c in str:
        counter += 1

        if (counter >= len and c == ' '):
            counter = 0
            split += '\n'

        else:
            split += c

    return split

# Displays statistics.
# - Percentage and number of queries where Jenaclone is faster, and how much faster.
# - Percentage and number of queries where Jenaclone is slower, and how much slower.
# - Result set size of the two groups.
# - Average size of BGPS of the two groups.
# - Presence of OPTIONAL in the two groups.
# - Number of variables in the two groups per query.
def display_stats(results, predicate):
    times = results

    if (predicate != None):
        times = list(filter(lambda time: predicate(time), times))

    no_timeouts = list(filter(lambda time: time.get_jena_time() != -1 and time.get_jenaclone_time() != -1 and time.get_leapfrog_time() != -1, times))

    jena_faster = list(filter(lambda time: time.get_jena_time() < min(time.get_jenaclone_time(), time.get_leapfrog_time()), no_timeouts))
    jenaclone_faster = list(filter(lambda time: time.get_jenaclone_time() <= min(time.get_jena_time(), time.get_leapfrog_time()), no_timeouts))
    leapfrog_faster = list(filter(lambda time: time.get_leapfrog_time() < min(time.get_jena_time(), time.get_jenaclone_time()), no_timeouts))

    jenaclone_better_than_jena = list(filter(lambda time: time.get_jenaclone_time() < time.get_jena_time() or (time.get_jenaclone_time() != -1 and time.get_jena_time() == -1), times))
    jenaclone_better_than_leapfrog = list(filter(lambda time: time.get_jenaclone_time() < time.get_leapfrog_time() or (time.get_jenaclone_time() != -1 and time.get_leapfrog_time() == -1), times))
    jena_better_than_jenaclone = list(filter(lambda time: time.get_jena_time() < time.get_jenaclone_time() or (time.get_jena_time != -1 and time.get_jenaclone_time() == -1), times))
    leapfrog_better_than_jenaclone = list(filter(lambda time: time.get_leapfrog_time() < time.get_jenaclone_time() or (time.get_leapfrog_time() != -1 and time.get_jenaclone_time() == -1), times))

    jenaclone_better_than_jena_lst = list(map(lambda time: time.get_jenaclone_time(), jenaclone_better_than_jena))
    jenaclone_better_than_leapfrog_lst = list(map(lambda time: time.get_jenaclone_time(), jenaclone_better_than_leapfrog))
    jena_better_than_jenaclone_lst = list(map(lambda time: time.get_jena_time(), jena_better_than_jenaclone))
    leapfrog_better_than_jenaclone_lst = list(map(lambda time: time.get_leapfrog_time(), leapfrog_better_than_jenaclone))

    total_amount = len(times)

    jena_avg_rs_size = 0
    jenaclone_avg_rs_size = 0
    leapfrog_avg_rs_size = 0
    jena_avg_var_count = 0
    jenaclone_avg_var_count = 0
    leapfrog_avg_var_count = 0
    jena_avg_bgp_size = 0
    jenaclone_avg_bgp_size = 0
    leapfrog_avg_bgp_size = 0

    if (len(jena_faster) > 0):
        jena_avg_rs_size = sum(map(lambda time: time.jena_resultset_size(), jena_faster)) / len(jena_faster)
        jena_avg_bgp_size = sum(map(lambda time: time.bgp_size(), jena_faster)) / len(jena_faster)
        jena_avg_var_count = sum(map(lambda time: time.get_variable_count(), jena_faster)) / len(jena_faster)

    if (len(jenaclone_faster) > 0):
        jenaclone_avg_rs_size = sum(map(lambda time: time.jenaclone_resultset_size(), jenaclone_faster)) / len(jenaclone_faster)
        jenaclone_avg_bgp_size = sum(map(lambda time: time.bgp_size(), jenaclone_faster)) / len(jenaclone_faster)
        jenaclone_avg_var_count = sum(map(lambda time: time.get_variable_count(), jenaclone_faster)) / len(jenaclone_faster)

    if (len(leapfrog_faster) > 0):
        leapfrog_avg_rs_size = sum(map(lambda time: time.leapfrog_resultset_size(), leapfrog_faster)) / len(leapfrog_faster)
        leapfrog_avg_bgp_size = sum(map(lambda time: time.bgp_size(), leapfrog_faster)) / len(leapfrog_faster)
        leapfrog_avg_var_count = sum(map(lambda time: time.get_variable_count(), leapfrog_faster)) / len(leapfrog_faster)

    jena_empty_result_set_count = len(list(filter(lambda t: t.jena_resultset_size() == 0, jena_faster)))
    jenaclone_empty_result_set_count = len(list(filter(lambda t : t.jenaclone_resultset_size() == 0, jenaclone_faster)))
    leapfrog_empty_result_set_count = len(list(filter(lambda t : t.leapfrog_resultset_size() == 0, leapfrog_faster)))

    jena_timeout_count = timeout_count(times, lambda time: time.get_jena_time())
    jenaclone_timeout_count = timeout_count(times, lambda time: time.get_jenaclone_time())
    leapfrog_timeout_count = timeout_count(times, lambda time: time.get_leapfrog_time())

    dictionary_checks = list(filter(lambda time: True in time.dictionary_usage(), no_timeouts))

    print(format_stat('Fastest Query Execution Distribution', str(len(jenaclone_faster) / total_amount) + ' - (' + str(len(jenaclone_faster)) + '/' + str(total_amount) + ')', str(len(jena_faster) / total_amount) + ' - (' + str(len(jena_faster)) + '/' + str(total_amount) + ')', str(len(leapfrog_faster) / total_amount) + ' - (' + str(len(leapfrog_faster)) + '/' + str(total_amount) + ')', False) + '\n')
    print(format_stat('Fastest Query Execution Distribution - Average resultset size per query', str(jenaclone_avg_rs_size), str(jena_avg_rs_size), str(leapfrog_avg_rs_size)) + '\n')
    print(format_stat('Fastest Query Execution Distribution - \'OPTIONAL\' presence count', str(optional_presence_count(jenaclone_faster)) + '/' + str(optional_presence_count(times)), str(optional_presence_count(jena_faster)) + '/' + str(optional_presence_count(times)), str(optional_presence_count(leapfrog_faster)) + '/' + str(optional_presence_count(times))) + '\n')
    print(format_stat('Fastest Query Execution Distribution - Average BGP size per query', str(jenaclone_avg_bgp_size), str(jena_avg_bgp_size), str(leapfrog_avg_bgp_size)) + '\n')
    print(format_stat('Fastest Query Execution Distribution - Average variable count per query', str(jenaclone_avg_var_count), str(jena_avg_var_count), str(leapfrog_avg_var_count)) + '\n')
    print(format_stat('Fastest Query Execution Distribution - Mean time difference from other triplestore (Jenaclone - Jena)', str(mean_time_diff(jenaclone_better_than_jena, lambda t: t.get_jena_time(), lambda t: t.get_jenaclone_time())), str(mean_time_diff(jena_better_than_jenaclone, lambda t: t.get_jenaclone_time(), lambda t: t.get_jena_time()))) + '\n')
    print(format_stat('Fastest Query Execution Distribution - Mean time difference from other triplestore (Jenaclone - Leapfrog)', str(mean_time_diff(jenaclone_better_than_leapfrog, lambda t: t.get_leapfrog_time(), lambda t: t.get_jenaclone_time())), str(mean_time_diff(leapfrog_better_than_jenaclone, lambda t: t.get_jenaclone_time(), lambda t: t.get_leapfrog_time()))) + '\n')
    print(format_stat('Fastest Query Execution Distribution - Median time difference from other triplestore (Jenaclone - Jena)', str(median_time_diff(jenaclone_better_than_jena, lambda t: t.get_jena_time(), lambda t: t.get_jenaclone_time())), str(median_time_diff(jena_better_than_jenaclone, lambda t: t.get_jenaclone_time(), lambda t: t.get_jena_time()))) + '\n')
    print(format_stat('Fastest Query Execution Distribution - Median time difference from other triplestore (Jenaclone - Leapfrog)', str(median_time_diff(jenaclone_better_than_leapfrog, lambda t: t.get_leapfrog_time(), lambda t: t.get_jenaclone_time())), str(median_time_diff(leapfrog_better_than_jenaclone, lambda t: t.get_jenaclone_time(), lambda t: t.get_leapfrog_time()))) + '\n')
    print(format_stat('Fastest Query Execution Distribution - Performance improvement (Jenaclone vs Jena)', str(avg_improvement(jenaclone_better_than_jena_lst, list(map(lambda time: time.get_jena_time(), jenaclone_better_than_jena)))), str(avg_improvement(jena_better_than_jenaclone_lst, list(map(lambda time: time.get_jenaclone_time(), jena_better_than_jenaclone))))) + '\n')
    print(format_stat('Fastest Query Execution Distribution - Performance improvement (Jenaclone vs Leapfrog)', str(avg_improvement(jenaclone_better_than_leapfrog_lst, list(map(lambda time: time.get_leapfrog_time(), jenaclone_better_than_leapfrog)))), str(avg_improvement(leapfrog_better_than_jenaclone_lst, list(map(lambda time: time.get_jenaclone_time(), leapfrog_better_than_jenaclone))))) + '\n')
    print(format_stat('Fastest Query Execution Distribution - Performance improvement median (Jenaclone vs Jena)', str(median_improvement(jenaclone_better_than_jena_lst, list(map(lambda time: time.get_jena_time(), jenaclone_better_than_jena)))), str(median_improvement(jena_better_than_jenaclone_lst, list(map(lambda time: time.get_jenaclone_time(), jena_better_than_jenaclone))))) + '\n')
    print(format_stat('Fastest Query Execution Distribution - Performance improvement median (Jenaclone vs Leapfrog)', str(median_improvement(jenaclone_better_than_leapfrog_lst, list(map(lambda time: time.get_leapfrog_time(), jenaclone_better_than_leapfrog)))), str(median_improvement(leapfrog_better_than_jenaclone_lst, list(map(lambda time: time.get_jenaclone_time(), leapfrog_better_than_jenaclone))))) + '\n')
    print(format_stat('Fastest Query Execution Distribution - Number of empty result set sizes', str(jenaclone_empty_result_set_count), str(jena_empty_result_set_count), str(leapfrog_timeout_count)) + '\n')
    print(format_stat('Timeout count', str(jenaclone_timeout_count), str(jena_timeout_count), str(leapfrog_timeout_count)) + '\n')
    print(format_stat('Fastest Query Execution Distribution With Dictionary Check (at least one positive check)', str(dictionary_check_count(dictionary_checks, lambda time: time.get_jenaclone_time(), lambda time: [time.get_jena_time(), time.get_leapfrog_time()])) + '/' + str(len(dictionary_checks)), str(dictionary_check_count(dictionary_checks, lambda time: time.get_jena_time(), lambda time: [time.get_jenaclone_time(), time.get_leapfrog_time()])) + '/' + str(len(dictionary_checks)), str(dictionary_check_count(dictionary_checks, lambda time: time.get_leapfrog_time(), lambda time: [time.get_jenaclone_time(), time.get_jena_time()]))) + '/' + str(len(dictionary_checks)) + '\n')

# Number of presences of OPTIONAL.
def optional_presence_count(times):
    count = 0

    for time in times:
        if ('OPTIONAL' in time.get_query()):
            count += 1

    return count

# Computes mean difference in benchmark times.
# Always computes time of Jena subtracted by time of Jenaclone.
def mean_time_diff(times, get_first, get_second):
    if (len(times) == 0):
        return 0

    mean = 0

    for time in times:
        if (get_first(time) == -1 or get_second(time) == -1):
            continue

        mean += get_first(time) - get_second(time)

    return float(mean) / len(times)

# Computes median time difference in benchmark times.
# Always computes time of Jena subtracted by time of Jenaclone.
def median_time_diff(times, get_first, get_second):
    if (len(times) == 0):
        return 0

    time_diffs = map(lambda t: get_first(t) - get_second(t) if get_first(t) != -1 and get_second(t) != -1 else 0, times)
    return statistics.median(time_diffs)

# Computes a list of improvements.
def improvements(better, than):
    imprs = list()

    for i in range(len(better)):
        if (better[i] == -1 or than[i] == -1):
            continue

        imprs.append(float(than[i] - better[i]) / than[i])

    return imprs

# Computes average improvement.
# Both argument lists must be of same length.
def avg_improvement(better, than):
    total = 0
    imprs = improvements(better, than)

    if (len(imprs) == 0):
        return 0

    for impr in imprs:
        total += impr

    return float(total) / len(imprs)

# Computes median improvement.
# Both argument lists must be of same length.
def median_improvement(better, than):
    imprs = improvements(better, than)

    if (len(imprs) == 0):
        return 0

    return statistics.median(imprs)

# Number of queries that timed out
def timeout_count(times, getter):
    count = 0

    for time in times:
        if (getter(time) == -1):
            count += 1

    return count

# Count number of queries that are faster that used at least on positive dictionary check in Jenaclone
def dictionary_check_count(times, get_db_time, get_other_db_times):
    counter = 0

    for time in times:
        if (True in time.dictionary_usage() and get_db_time(time) < min(get_other_db_times(time))):
            counter += 1

    return counter

# Main.
if __name__ == "__main__":
    if (len(sys.argv) <= 1):
        raise "Missing query folder names."

    folders = list()

    for i in range(len(sys.argv) - 1):
        folders.append(sys.argv[i + 1])

    folders_exist_check(folders)

    results = list()

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

            for i in range(len(queries)):
                results.append(Time(jena_file, jenaclone_file, leapfrog_file, queries[i], jena_times[i][1], jenaclone_times[i][1], leapfrog_times[i][1], jena_times[i][0], jenaclone_times[i][0], leapfrog_times[i][0], []))

    output_lines = list()

#    with open(BENCHMARK_OUTPUT, "r") as output:
#        for line in output:
#            output_lines.append(line)

#    check_for_dictionary_use(results, output_lines)
    time_min = 100
    results.sort(key = lambda time: time.get_jenaclone_time())
    display_times(results, lambda time: time.get_jena_time() >= time_min or time.get_jenaclone_time() >= time_min or time.get_leapfrog_time() >= time_min)
