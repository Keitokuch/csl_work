#!/usr/bin/python

from __future__ import print_function
from bcc import BPF, PerfType, PerfSWConfig
from time import sleep, strftime
from tempfile import NamedTemporaryFile
from os import open, close, dup, unlink, O_WRONLY

debug = 0
frequency = 99
countdown = 5

# initialize BPF & perf_events
b = BPF(src_file=b'runqlen.c')
b.attach_perf_event(ev_type=PerfType.SOFTWARE,
    ev_config=PerfSWConfig.CPU_CLOCK, fn_name="do_perf_event",
    sample_period=0, sample_freq=frequency)

def handler(cpu, data, size):
    event = b['events'].event(data)
    print(event.cpu, event.h_nr_running, event.runnable_weight, event.weight)

print("Sampling run queue length... Hit Ctrl-C to end.")

b['events'].open_perf_buffer(handler)

exiting = 0
#  dist = b.get_table("dist")
while (1):
    try:
        b.perf_buffer_poll()
        #  sleep(2)
    except KeyboardInterrupt:
        exiting = 1

    #  print()
    #  # run queue length histograms
    #  dist.print_linear_hist("runqlen", "cpu")

    #  dist.clear()

    #  countdown -= 1
    #  if exiting or countdown == 0:
    #      exit()
    if exiting:
        exit()
