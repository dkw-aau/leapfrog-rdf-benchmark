# Computes mean and median improvement of queries faster in JenaBloom compared to queries faster in Jena

import statistics
import os

groups = ['bgps', 'existence_check', 'optionals', 'specialized', 'modified_bgps']
jena = list()
jenaclone = list()

for group in groups:
    types = os.listdir(group)

    for type in types:
        results_path = group + '/' + type + '/'
        versions = ['jena.csv', 'jenaclone.csv']

        for version in versions:
            first = True
            with open(results_path + version, 'r') as file:
                for line in file:
                    if first:
                        first = False
                        continue

                    elif 'timeout' in line:
                        continue

                    ms = 1000000
                    time_ms = float(line.strip().split(',')[2]) / ms

                    if version == 'jena.csv':
                        jena.append(time_ms)

                    else:
                        jenaclone.append(time_ms)

jena_best = list()
jenaclone_best = list()

for i in range(len(jena)):
    if jena[i] < jenaclone[i]:
        jena_best.append(jena[i])

    else:
        jenaclone_best.append(jenaclone[i])

jena_best_avg = statistics.mean(jena_best)
jenaclone_best_avg = statistics.mean(jenaclone_best)
jena_best_median = statistics.median(jena_best)
jenaclone_best_median = statistics.median(jenaclone_best)

improvement_avg = (jena_best_avg - jenaclone_best_avg) / jena_best_avg
improvement_median = (jena_best_median - jenaclone_best_median) / jena_best_median

print('Mean improvement: ' + str(improvement_avg * 100) + '%')
print('Median improvement: ' + str(improvement_median * 100) + '%')
