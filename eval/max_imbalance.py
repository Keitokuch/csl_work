#!/usr/bin/env python3

from bcc import BPF, PerfType, PerfSWConfig
from time import sleep
import sys
import logging
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--tag', help='tag for output')
parser.add_argument('-o', '--output', help='output file name (overwrites -t)')
parser.add_argument('-a', '--append', action='store_true', help='append to output')
args = parser.parse_args()

frequency = 500

write_file = args.output or args.tag and f'imbalance_{args.tag}.json' or 'imbalance.json'

#  cm_events = []
#  latency_datasource = FuncLatencyDatasource(append=args.append,
#                                             write_file=write_file)

bpf_text = "max_imbalance.c"

# initialize BPF & probes
b = BPF(src_file=bpf_text)
b.attach_perf_event(ev_type=PerfType.SOFTWARE,
    ev_config=PerfSWConfig.CPU_CLOCK, fn_name="do_perf_event",
    sample_period=0, sample_freq=frequency)



logger = logging.getLogger('dump')
fhdlr = logging.FileHandler('dump.log')
shdlr = logging.StreamHandler()
logger.addHandler(fhdlr)
logger.addHandler(shdlr)

hist = b.get_table("hist")
while True:
    try:
        sleep(0.5)
    except KeyboardInterrupt:
        exit()

    rqlen = [k.value for k in hist]
    print(rqlen)
    maxlen, minlen = max(rqlen), min(rqlen)
    imbalance = maxlen - minlen
    print(imbalance)
    hist.clear()
