#!/usr/bin/env python3

from bcc import BPF
import sys

from datasource_old import scheduler, NR_CPU

# initialize BPF & probes
b = BPF(src_file='bcc_sched.c')

#  updates = {}
updates = []
_rqs = list(range(NR_CPU))

# perf buffer callbacks

def tn_handler(cpu, data, size):
    event = b['tn_events'].event(data)
    #  global updates
    #  updates[event.ts] = ('new', (event.pid, event.comm))
    event.type = 'new'
    scheduler.update(event)


def td_handler(cpu, data, size):
    event = b['td_events'].event(data)
    event.type = 'dead'
    scheduler.update(event)


def eq_handler(cpu, data, size):
    event = b['eq_events'].event(data)
    #  pids = event.pids[:event.pid_cnt]
    #  weights = event.weights[:event.pid_cnt]
    #  global updates
    updates.append((event.ts, ('eq', event.pid, event.cpu, event.qc,
                               event.comm, event.runnable_weight)))
    print(event.ts, 'eq')
    #  updates[event.ts] = ('eq', (event.pid, event.cpu, event.qc,
                                #  event.comm, event.runnable_weight))


def dq_handler(cpu, data, size):
    event = b['dq_events'].event(data)
    #  pids = event.pids[:event.pid_cnt]
    #  weights = event.weights[:event.pid_cnt]
    #  global updates
    updates.append((event.ts, ('dq', event.pid, event.cpu, event.qc)))
    print(event.ts, 'dq')
    #  updates[event.ts] = ('dq', (event.pid, event.cpu, event.qc))


def rn_handler(cpu, data, size):
    event = b['rn_events'].event(data)
    #  global updates
    updates.append((event.ts, ('rn', event.pid, event.comm)))
    #  updates[event.ts] = ('rn', (event.pid, event.comm))


def rq_handler(cpu, data, size):
    event = b['rq_events'].event(data)
    pids = event.pids[:event.pid_cnt]
    weights = event.weights[:event.pid_cnt]
    cpu = event.cpu
    #  global updates
    try:
        _rqs.remove(cpu)
        #  updates[event.ts] = ('rq', (event.cpu, pids, event.runnable_weight, event.len))
        updates.append((event.ts, ('rq', event.cpu, pids, event.runnable_weight, event.len)))
        print('remove', cpu)
    except ValueError:
        pass


def tsk_handler(cpu, data, size):
    event = b['tsk_events'].event(data)
    global updates
    #  updates[event.ts] = ('tsk', (event.pid, event.comm, event.runnable_weight))


def locality_handler(cpu, data, size):
    event = b['locality_events'].event(data)


# set up perf buffers
#  b['dq_events'].open_perf_buffer(dq_handler)
#  b['eq_events'].open_perf_buffer(eq_handler)
#  b['rq_events'].open_perf_buffer(rq_handler, page_cnt=2)
#  b['tsk_events'].open_perf_buffer(tsk_handler)
#  b['cs_events'].open_perf_buffer(cs_handler)
b['tn_events'].open_perf_buffer(tn_handler)
b['td_events'].open_perf_buffer(td_handler)
#  b['locality_events'].open_perf_buffer(locality_handler)
#  b['rn_events'].open_perf_buffer(rn_handler)

#  b['te_events'].open_perf_buffer(te_handler)

from time import sleep
last_ts = 0
#  while True:
for i in range(30000):
    b.perf_buffer_poll()
    #  if not _rqs:
        #  del b['rq_events']
        #  _rqs = True
    #  if i % 50000 == 0:
        #  print(scheduler.tasks)
