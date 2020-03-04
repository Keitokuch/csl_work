#! /usr/bin/env python3
NUMA_PATH='/sys/devices/system/node/'

with open(NUMA_PATH+'possible') as f:
    line = f.readlines()[0].strip()
    node_range = list(map(int, line.split('-')))
    node_list = range(node_range[0], node_range[1] + 1)

node_cpulist = {}
for node in node_list:
    node_dir = NUMA_PATH + f'node{str(node)}/'
    node_cpulist[node] = []
    with open(node_dir + 'cpulist') as f:
        line = f.readlines()[0].strip()
        for range_str in line.split(','):
            cpu_range = list(map(int, range_str.split('-')))
            cpu_list = range(cpu_range[0], cpu_range[1] + 1)
            node_cpulist[node] += cpu_list

cpu_nodemap = {}
for node, cpulist in node_cpulist.items():
    for cpu in cpulist:
        cpu_nodemap[cpu] = node

print(node_cpulist)
print(cpu_nodemap)
