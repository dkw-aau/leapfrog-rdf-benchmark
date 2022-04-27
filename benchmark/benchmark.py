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

for query in queries:
    count = 0
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

        sparql.setQuery(query.replace("(COUNT(*) AS ?count)", "*"))
        projection_results = sparql.query().convert()

        for result in projection_results["results"]["bindings"]:
            count += 1

        print("{0};{1};{2}".format(query_number, count, avg_elapsed_time))

    except Exception as e:
        print("{0};{1};timeout".format(query_number, count))
        traceback.print_exc()

    query_number += 1
