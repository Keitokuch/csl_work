#!/usr/bin/env python3

from bcc import BPF
import argparse
from time import sleep

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--tag', help='tag for output')
parser.add_argument('-o', '--output', help='output file name (overwrites -t)')
parser.add_argument('-a', '--append', action='store_true', help='append to output')
parser.add_argument('-s', '--write_size', type=int, action='store')
parser.add_argument('--old', action='store_true', help='original kernel')
args = parser.parse_args()

write_file = args.output or args.tag and f'runqlen_{args.tag}.csv' or 'runqlen_output.csv'

bpf_text = 'runqlen.c'

# initialize BPF & probes
b = BPF(src_file=bpf_text)

hist = b.get_table("hist")
while True:
    try:
        sleep(3)
    except KeyboardInterrupt:
        hist_rqlen = {k.value: v.value for k, v in hist.items()}
        print(hist_rqlen)
        exit()
