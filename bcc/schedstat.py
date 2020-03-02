#!/usr/bin/env python3

#  from __future__ import print_function
from bcc import BPF
from time import sleep
import sys

#  from sched import rq, task, rqs, tasks

# initialize BPF & probes
b = BPF(src_file='schedstat.c')
#  b.attach_kprobe(event="finish_task_switch", fn_name="trace_context_switch")
#  b.attach_kprobe(event="wake_up_new_task", fn_name="trace_new_task")
#  b.attach_kretprobe(event="enqueue_task_fair", fn_name="trace_rq")
#  b.attach_kretprobe(event="dequeue_task_fair", fn_name="trace_rq")

times = []
#  b.attach_kprobe(event="perf_event_exit_task", fn_name="trace_exit")

# perf buffer callbacks
def cs_handler(cpu, data, size):
    event = b['cs_events'].event(data)
    pids = event.pids[:event.pid_cnt]
    weights = event.weights[:event.pid_cnt]
    times.append(event.ts)
    print(event.ts, cpu, 'cs', event.p_pid, 'to', event.n_pid, event.comm, event.len, event.pid_cnt,
          'prev', event.curr_pid, 'state', event.prev_state, pids, weights)


def tn_handler(cpu, data, size):
    event = b['tn_events'].event(data)
    print(event.ts, cpu, 'new', event.pid, event.comm)


def td_handler(cpu, data, size):
    event = b['td_events'].event(data)
    print(event.ts, cpu, 'dead', event.pid, event.comm)


def eq_handler(cpu, data, size):
    event = b['eq_events'].event(data)
    pids = event.pids[:event.pid_cnt]
    weights = event.weights[:event.pid_cnt]
    times.append(event.ts)
    print(event.ts, event.qc_cpu, 'eq', event.qc_pid, 'state', event.qc_flags, event.len, event.pid_cnt, event.runnable_weight,
          event.curr_pid, event.comm, pids, weights, f'qc{event.qc_len}', event.before_len)
    #  print(event.qc_len)


def dq_handler(cpu, data, size):
    event = b['dq_events'].event(data)
    pids = event.pids[:event.pid_cnt]
    weights = event.weights[:event.pid_cnt]
    times.append(event.ts)
    print(event.ts, event.qc_cpu, 'dq', event.qc_pid, 'state', event.qc_flags, event.len, event.pid_cnt, event.runnable_weight,
          event.curr_pid, event.comm, pids, weights, f'qc{event.qc_len}', event.before_len)
    #  print(event.qc_len)


def lb_handler(cpu, data, size):
    event = b['lb_events'].event(data)
    print(event.ts, cpu, 'lb', event.pid, event.comm, 'from', event.src_cpu, 'to', event.dst_cpu)


def rn_handler(cpu, data, size):
    event = b['rn_events'].event(data)
    print(event.ts, cpu, 'rename', event.pid, event.oldcomm, 'to', event.comm)


def locality_handler(cpu, data, size):
    event = b['locality_events'].event(data)
    print(event.ts, cpu, 'can_migrate', event.pid, 'from', event.src_cpu,
          'to', event.dst_cpu, '?', event.degrades_locality)


# set up perf buffers
#  b['lb_events'].open_perf_buffer(lb_handler)
b['dq_events'].open_perf_buffer(dq_handler)
b['eq_events'].open_perf_buffer(eq_handler)
b['cs_events'].open_perf_buffer(cs_handler)
#  b['tn_events'].open_perf_buffer(tn_handler)
#  b['td_events'].open_perf_buffer(td_handler)
#  b['locality_events'].open_perf_buffer(locality_handler)
#  b['rq_events'].open_perf_buffer(rq_handler)
#  b['rn_events'].open_perf_buffer(rn_handler)

#  b['te_events'].open_perf_buffer(te_handler)

import warnings
ready = 0
b.perf_buffer_poll()
lt = 0
while True:
    #  for _ in range(10000):
    try:
        b.perf_buffer_poll()
        times = sorted(times)
        ft = times[0]
        if ft < lt:
            print("decreasing time", ft, lt)
        lt = times[-1]
    except KeyboardInterrupt:
        exit()
    if not ready:
        warnings.warn('ready')
        ready = 1
    times = []
    print('==')
