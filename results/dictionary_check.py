from parser import Time

# Attaches dictionary check flag to queries that used the dictionary.
# Arguments are list of Time instances and benchmark output string lines as a list.
def check_for_dictionary_use(times, benchmark_output):
    line_count = 0

    for i in range(len(benchmark_output)):
        line = benchmark_output[i]
        bgp = None

        if ("Query =" in line):
            bgp = line[line.find("{"):line.find("}") + 1]

        if (bgp != None and "OK" in benchmark_output[i + 1]):
            i += 2
            continue

        elif (bgp != None and "DICTIONARY" in benchmark_output[i + 1]):
            i += 1

            while (i < len(benchmark_output) and "DICTIONARY" in benchmark_output[i]):
                val = False

                if ("true" in benchmark_output[i]):
                    val = True

                insert_dictionary_value(times, bgp, val)
                i += 1

            bgp = None

    clean_values(times)

def insert_dictionary_value(times, bgp, value):
    for time in times:
        query = time.get_query()

        if (query[query.find("{"):query.find("}") + 1] == bgp):
            time.add_dictionary_usage(value)
            return

# Each query is executed four times, so we need to divide the number of dictionary usages by four for each type
def clean_values(times):
    for time in times:
        positives = list(filter(lambda t: t == True, time.dictionary_usage()))
        negatives = list(filter(lambda t: t == False, time.dictionary_usage()))
        time.dictionary_usage().clear()

        for i in range(int(float(len(positives)) / 4)):
            time.add_dictionary_usage(positives[i])

        for i in range(int(float(len(negatives)) / 4)):
            time.add_dictionary_usage(negatives[i])
