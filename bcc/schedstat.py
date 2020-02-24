#!/usr/bin/env python

from __future__ import print_function
from bcc import BPF, printb
from time import sleep
import sys

# initialize BPF & probes
b = BPF(src_file=b'schedstat.c')
#  b.attach_kprobe(event="finish_task_switch", fn_name="trace_context_switch")
#  b.attach_kprobe(event="wake_up_new_task", fn_name="trace_new_task")
#  b.attach_kretprobe(event="enqueue_task_fair", fn_name="trace_rq")
#  b.attach_kretprobe(event="dequeue_task_fair", fn_name="trace_rq")

#  b.attach_kprobe(event="perf_event_exit_task", fn_name="trace_exit")

# perf buffer callbacks
def cs_handler(cpu, data, size):
    event = b['cs_events'].event(data)
    pids = event.pids[:event.pid_cnt]
    weights = event.weights[:event.pid_cnt]
    print(event.ts, cpu, 'cs', event.p_pid, 'to', event.n_pid, event.comm, event.len, event.pid_cnt, 
          'prev', event.curr_pid, 'state', event.prev_state, pids, weights)


def tn_handler(cpu, data, size):
    event = b['tn_events'].event(data)
    print(event.ts, cpu, 'new', event.pid, event.comm, event.cpu)


def td_handler(cpu, data, size):
    event = b['td_events'].event(data)
    print(event.ts, cpu, 'dead', event.pid, event.comm)


#  def te_handler(cpu, data, size):
#      event = b['td_events'].event(data)
#      print(event.ts, cpu, 'edead', event.pid, event.tgid)


def rq_handler(cpu, data, size):
    event = b['rq_events'].event(data)
    enqueue = 'eq' if event.enqueue == 1 else 'dq'
    pids = event.pids[:event.pid_cnt]
    weights = event.weights[:event.pid_cnt]
    print(event.ts, cpu, enqueue, event.qc_pid, event.len, event.pid_cnt, event.runnable_weight,
          event.curr_pid, event.comm, pids, weights)

def eq_handler(cpu, data, size):
    event = b['eq_events'].event(data)
    pids = event.pids[:event.pid_cnt]
    weights = event.weights[:event.pid_cnt]
    if event.len != event.pid_cnt:
        sys.exit()
    print(event.ts, event.qc_cpu, 'eq', event.qc_pid, 'state', event.qc_flags, event.len, event.pid_cnt, event.runnable_weight,
          event.curr_pid, event.comm, pids, weights)


def dq_handler(cpu, data, size):
    event = b['dq_events'].event(data)
    pids = event.pids[:event.pid_cnt]
    weights = event.weights[:event.pid_cnt]
    print(event.ts, event.qc_cpu, 'dq', event.qc_pid, 'state', event.qc_flags, event.len, event.pid_cnt, event.runnable_weight,
          event.curr_pid, event.comm, pids, weights)

def lb_handler(cpu, data, size):
    event = b['lb_events'].event(data)
    print(event.ts, cpu, 'lb', event.pid, event.comm, 'from', event.src_cpu, 'to', event.dst_cpu)


def rn_handler(cpu, data, size):
    event = b['rn_events'].event(data)
    print(event.ts, cpu, 'rename', event.pid, event.oldcomm, 'to', event.comm)

def test_handler(cpu, data, size):
    event = b['yield_events'].event(data)
    print(event.ts, cpu, 'yeild', event.cpu, event.pid)


# set up perf buffers
b['lb_events'].open_perf_buffer(lb_handler)
b['dq_events'].open_perf_buffer(dq_handler)
b['eq_events'].open_perf_buffer(eq_handler)
b['cs_events'].open_perf_buffer(cs_handler)
b['tn_events'].open_perf_buffer(tn_handler)
b['td_events'].open_perf_buffer(td_handler)
b['yield_events'].open_perf_buffer(test_handler)
#  b['rq_events'].open_perf_buffer(rq_handler)
b['rn_events'].open_perf_buffer(rn_handler)

#  b['te_events'].open_perf_buffer(te_handler)

import warnings
ready = 0
#  for _ in range(1000):
b.perf_buffer_poll()
while True:
    b.perf_buffer_poll()
    if not ready:
        warnings.warn('ready')
        ready = 1
    print('==')
