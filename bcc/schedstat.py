#!/usr/bin/env python

from __future__ import print_function
from bcc import BPF

# initialize BPF & probes
b = BPF(src_file=b'schedstat.c')
b.attach_kprobe(event="finish_task_switch", fn_name="trace_context_switch")
b.attach_kprobe(event="enqueue_task_fair", fn_name="trace_enqueue_task")
b.attach_kprobe(event="dequeue_task_fair", fn_name="trace_dequeue_task")
b.attach_kprobe(event="wake_up_new_task", fn_name="trace_new_task")
b.attach_kprobe(event="do_task_dead", fn_name="trace_dead")
#  b.attach_kprobe(event="perf_event_exit_task", fn_name="trace_exit")
b.attach_kretprobe(event="enqueue_task_fair", fn_name="trace_rq")
b.attach_kretprobe(event="dequeue_task_fair", fn_name="trace_rq")

# perf buffer callbacks
def cs_handler(cpu, data, size):
    event = b['cs_events'].event(data)
    print(event.ts, cpu, event.p_pid, 'to', event.n_pid)


def eq_handler(cpu, data, size):
    event = b['eq_events'].event(data)
    print(event.ts, cpu, 'en', event.cpu, event.pid, event.tgid)


def dq_handler(cpu, data, size):
    event = b['dq_events'].event(data)
    print(event.ts, cpu, 'de', event.cpu, event.pid, event.tgid)


def tn_handler(cpu, data, size):
    event = b['tn_events'].event(data)
    print(event.ts, cpu, 'new', event.pid, event.tgid)


def td_handler(cpu, data, size):
    event = b['td_events'].event(data)
    print(event.ts, cpu, 'dead', event.pid, event.tgid)

#  def te_handler(cpu, data, size):
#      event = b['td_events'].event(data)
#      print(event.ts, cpu, 'edead', event.pid, event.tgid)


def rq_handler(cpu, data, size):
    event = b['rq_events'].event(data)
    print(event.ts, cpu, 'rq', event.len, event.runnable_weight)


# set up perf buffers
b['cs_events'].open_perf_buffer(cs_handler)
b['eq_events'].open_perf_buffer(eq_handler)
b['dq_events'].open_perf_buffer(dq_handler)
b['tn_events'].open_perf_buffer(tn_handler)
b['td_events'].open_perf_buffer(td_handler)
b['rq_events'].open_perf_buffer(rq_handler)

#  b['te_events'].open_perf_buffer(te_handler)

while True:
    b.perf_buffer_poll()
