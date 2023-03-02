import os
import random

base = 'queries/'
gt = 'ml/gt/'
test = 'ml/test/'
test_split = 0.2

folders = os.listdir(base)

for folder in folders:
    if '.' in folder:
        continue

    path = base + folder + '/'
    query_files = os.listdir(path)
    os.mkdir(gt + folder)
    os.mkdir(test + folder)

    for file in query_files:
        if '.' not in file:
            continue

        queries = list()

        # Read queries
        with open(path + file, 'r') as input:
            for line in input:
                queries.append(line.strip())

        # Gen training set
        with open(gt + folder + '/' + file, 'w') as output:
            num_queries = len(queries)
            gt_queries = list()

            while len(gt_queries) / num_queries < (1 - test_split):
                idx = random.randint(0, len(queries) - 1)
                gt_queries.append(queries[idx])
                del queries[idx]

            for gt_query in gt_queries:
                output.write(gt_query + '\n')

        # Gen test set
        with open(test + folder + '/' + file, 'w') as output:
            for query in queries:
                output.write(query + '\n')
