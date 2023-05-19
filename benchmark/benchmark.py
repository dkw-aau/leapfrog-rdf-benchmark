from SPARQLWrapper import SPARQLWrapper, JSON
import time
import traceback
import sys
import os

sparql = SPARQLWrapper(sys.argv[2])
sparql.setTimeout(1200)
sparql.setReturnFormat(JSON)

queries_file = open(sys.argv[1], "r")
queries = []
query_number = 0

for line in queries_file:
    queries.append(line.strip())

print('index,results,average time (3)')

for query in queries:
    time_sum = 0
    results = None

    try:
        sparql.setQuery(query)

        for i in range(3):
            start_time = time.time()
            results = sparql.query()
            elapsed_time = int((time.time() - start_time) * 1000000000)
            time_sum += elapsed_time

        avg_elapsed_time = int(time_sum / 3)

        json_results = results.convert()
        results_size = 0

        if "count" in json_results["results"]["bindings"][0]:
            results_size = int(json_results["results"]["bindings"][0]["count"]["value"])

        print("{0},{1},{2}".format(query_number, results_size, avg_elapsed_time))

    except Exception as e:
        print("{0},0,-1".format(query_number))
        traceback.print_exc()

    query_number += 1
