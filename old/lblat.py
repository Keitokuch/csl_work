#! /usr/bin/env python3

from bcc import BPF
from time import sleep

interval = 1
exiting = 0

b = BPF(src_file="lblat.c")

dist = b.get_table("dist")
while True:
    try:
        sleep(interval)
    except KeyboardInterrupt:
        exiting = 1

    print()
    #  dist.print_log2_hist('usecs', "", section_print_fn=int)
    dist.print_log2_hist('nanosecs', "", section_print_fn=int)
    dist.clear()
    if exiting:
        exit()
