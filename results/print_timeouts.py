import os

groups = ['bgps', 'empty', 'existence_check', 'optionals', 'specialized', 'modified_bgps']

for group in groups:
    print(group)

    types = os.listdir(group)

    for type in types:
        print('\n' + type)

        results_path = group + '/' + type + '/'
        versions = os.listdir(results_path)

        for version in versions:
            timeouts = 0
            first = True
            print('\n' + version)

            with open(results_path + version, 'r') as file:
                for line in file:
                    if first:
                        first = False
                        continue

                    elif 'timeout' in line:
                        timeouts += 1
                        continue

            print(timeouts)

    print('\n')
