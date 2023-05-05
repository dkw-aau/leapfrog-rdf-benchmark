import json

filename = 'gt_runtimes_validation_without.txt'
runtimes = dict()

with open(filename, 'r') as file:
    runtime = None
    bgp = None

    for line in file:
        if 'ERROR [' in line:
            tmp_line = line[line.find('ERROR'):]
            bgp_start = tmp_line.find('[')
            bgp_end = tmp_line.find(']')
            bgp = tmp_line[bgp_start:bgp_end + 1].replace('@', '')
            runtime = int(tmp_line[tmp_line.find(']:') + 3:])

        elif 'ERROR SIZE' in line and runtime is not None and bgp is not None:
            tmp_line = line[line.find('->'):]
            size = int(tmp_line[tmp_line.find(']:') + 3:])

            if bgp not in runtimes.keys():
                runtimes[bgp] = list()

            runtimes[bgp].append({'runtime': runtime, 'results': size})
            bgp = None
            runtime = None

results = dict()

for key in runtimes.keys():
    sum = 0

    for v in runtimes[key]:
        sum += v['runtime']

    results[key] = {'runtime': sum / len(runtimes[key]), 'results': runtimes[key][0]['results']}

with open('runtimes_without_blf.json', 'w') as file:
    json.dump(results, file)
