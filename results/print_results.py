import os

groups = ['bgps', 'empty', 'existence_check', 'optionals', 'specialized']

for group in groups:
    print(group)

    types = os.listdir(group)

    for type in types:
        print('\n' + type)

        results_path = group + '/' + type + '/'
        versions = os.listdir(results_path)

        for version in versions:
            first = True
            print('\n' + version)

            with open(results_path + version, 'r') as file:
                for line in file:
                    if first:
                        first = False
                        continue

                    elif 'timeout' in line:
                        continue

                    ms = 1000000
                    time_ms = float(line.strip().split(',')[2]) / ms

                    if time_ms >= 100:
                        print(str(time_ms).replace('.', ','))

    print('\n')
