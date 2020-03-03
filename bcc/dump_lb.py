#!/usr/bin/env python3

from bcc import BPF
import sys

from datasource import lb_context

# initialize BPF & probes
b = BPF(src_file='dump_lb.c')
#  b.attach_kprobe(event="can_migrate_task", fn_name="test_func")

# perf buffer callbacks
def lb_dst_handler(cpu, data, size):
    event = b['lb_dst_events'].event(data)
    pids = event.pids[:event.pid_cnt]
    #  print(event.instance_ts, 'lb_dst', event.cpu, event.h_nr_running,
          #  event.pid_cnt, event.runnable_weight, pids)

def lb_src_handler(cpu, data, size):
    event = b['lb_src_events'].event(data)
    pids = event.pids[:event.pid_cnt]
    #  print(event.instance_ts, 'lb_src', event.cpu, event.h_nr_running,
          #  event.pid_cnt, event.runnable_weight, pids)

def lb_env_handler(cpu, data, size):
    event = b['lb_env_events'].event(data)
    lb_context.update(event)
    #  print(event.instance_ts, 'lb_env', event.src_cpu, 'to', event.dst_cpu, event.imbalance)


def can_migrate_handler(cpu, data, size):
    event = b['can_migrate_events'].event(data)
    #  imbalance = lb_context.poll(event.instance_ts)['imbalance']
    #  print(event.instance_ts, 'can_migrate', event.pid, 'to', event.dst_cpu, '?', event.can_migrate, 'imbalance', imbalance)
    print(event.instance_ts, 'can', event.pid)



# set up perf buffers
b['lb_dst_events'].open_perf_buffer(lb_dst_handler)
b['lb_src_events'].open_perf_buffer(lb_src_handler)
b['lb_env_events'].open_perf_buffer(lb_env_handler)
b['can_migrate_events'].open_perf_buffer(can_migrate_handler)


while True:
#  for i in range(300):
    b.perf_buffer_poll()
