#!/usr/bin/python

from __future__ import print_function
from bcc import BPF
from time import sleep

is_support_raw_tp = BPF.support_raw_tracepoint()
print(is_support_raw_tp)


b = BPF(src_file=b'runqstat.c')
#  b.attach_kprobe(event="finish_task_switch", fn_name="do_trace")
#  b.attach_kprobe(event="enqueue_task_fair", fn_name="trace_enqueue_task")
b.attach_kprobe(event="set_task_rq_fair", fn_name="trace_set_task")

def handler(cpu, data, size):
    event = b['events'].event(data)
    print(event.h_nr_running_p, event.rw_p, event.h_nr_running_n, event.rw_n)

b['events'].open_perf_buffer(handler)

while (1):
    b.perf_buffer_poll()
