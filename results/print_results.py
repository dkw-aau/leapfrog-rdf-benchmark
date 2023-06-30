import os

groups = ['bgps', 'empty', 'existence_check', 'optionals', 'specialized', 'modified_bgps']

# Returns map from query shape in group to Jena version to list of runtimes
def get_results(group):
    shapes = os.listdir(group)
    shape_map = dict()

    for shape in shapes:
        shape_map[shape] = dict()
        results_path = group + '/' + shape + '/'
        versions = os.listdir(results_path)

        for version in versions:
            shape_map[shape][version] = list()
            first = True

            with open(results_path + version, 'r') as file:
                for line in file:
                    if first:
                        first = False
                        continue

                    elif 'timeout' in line:
                        shape_map[shape][version].append(-1)

                    else:
                        time_ms = float(line.strip().split(',')[2]) / 1000000	# Converted to ms
                        shape_map[shape][version].append(time_ms)

    return shape_map

# Returns None if everything is alright
# Otherwise, it returns a tuple indicating which query shape contains the size mis-match
def check_results_count(map):
    for shape in map.keys():
        size = len(map[shape][list(map[shape].keys())[0]])

        for version in map[shape].keys():
            if len(map[shape][version]) != size:
                return shape

    return None

# Filter results according to runtime of a given Jena version
def filter_runtimes(map, version, runtime):
    for shape in map.keys():
        positions = list()
        i = 0

        for time in map[shape][version]:
            if time != -1 and time < runtime:
                positions.append(i)

            i += 1

        positions.reverse()

        for version in map[shape].keys():
            for position in positions:
                map[shape][version].pop(position)

for group in groups:
    map = get_results(group)
    check = check_results_count(map)

    if check != None:
        print(check)
        break

    filter_runtimes(map, 'jena.csv', 100)
    print('\n' + group)

    for shape in map.keys():
        print('\n' + shape)

        for version in map[shape].keys():
            print('\n' + version)

            for time in map[shape][version]:
                print(str(time).replace('.', ','))
