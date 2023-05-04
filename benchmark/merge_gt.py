import json

runtimes_without = dict()
runtimes_with = dict()
gt = dict()
do_exist = 0
dont_exist = 0
conflicts = 0

with open('runtimes_without_blf.json', 'r') as file:
    runtimes_without = json.load(file)

with open('runtimes_with_blf.json', 'r') as file:
    runtimes_with = json.load(file)

for bgp in runtimes_without.keys():
    if not bgp in runtimes_with.keys():
        dont_exist += 1

    else:
        do_exist += 1
        if bgp in gt and gt[bgp]['with_runtime'] != runtimes_with[bgp]['runtime']:
            conflicts += 1

        gt[bgp] = {'with_runtime': runtimes_with[bgp]['runtime'], 'without_runtime': runtimes_without[bgp]['runtime'], 'with_size': runtimes_with[bgp]['results'], 'without_size': runtimes_without[bgp]['results']}

print('BGPS in original Jena also in Jena Bloom: ' + str(do_exist))
print('BGPS in original Jena not in Jena Bloom: ' + str(dont_exist))
print('There were ' + str(conflicts) + ' conflicts!')

with open('gt.json', 'w') as file:
    json.dump(gt, file)
