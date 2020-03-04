#!/usr/bin/env python3

from bcc import BPF
import sys

from datasource import can_migrate_datasource

NR_NODES=2

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
    #  lb_context.update(event)
    task_faults = event.p_numa_faults[:NR_NODES]
    print(event.instance_ts, 'try_migrate', event.pid, event.src_cpu, 'to', event.dst_cpu, event.imbalance, event.env_idle)
    print('            p', event.delta, event.numa_preferred_nid, event.p_policy, event.p_running)
    #  print('         lens', event.src_nr_running, event.src_nr_numa_running, event.src_nr_preferred_running)
    #  print('       faults', task_faults)


def can_migrate_handler(cpu, data, size):
    event = b['can_migrate_events'].event(data)
    #  imbalance = lb_context.poll(event.instance_ts)['imbalance']
    can_migrate_datasource.update(event)


# set up perf buffers
#  b['lb_dst_events'].open_perf_buffer(lb_dst_handler)
#  b['lb_src_events'].open_perf_buffer(lb_src_handler)
#  b['lb_env_events'].open_perf_buffer(lb_env_handler)
b['can_migrate_events'].open_perf_buffer(can_migrate_handler)


while True:
    try:
        b.perf_buffer_poll()
    except KeyboardInterrupt:
        print(can_migrate_datasource.dump())
        exit()
