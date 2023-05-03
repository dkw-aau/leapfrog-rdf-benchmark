import json

filename = 'gt_runtime_without_blf.txt'
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
            runtimes[bgp] = {'runtime': runtime, 'results': size}
            bgp = None
            runtime = None

with open('runtimes_without_blf.json', 'w') as file:
    json.dump(runtimes, file)
