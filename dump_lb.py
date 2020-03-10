#!/usr/bin/env python3

from bcc import BPF
import sys
import logging

from datasource import CanMigrateData

NR_NODES=2

cm_events = []
can_migrate_datasource = CanMigrateData(append=True, write_size=1000, write_file='list_dump.csv')

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


def can_migrate_handler(cpu, data, size):
    event = b['can_migrate_events'].event(data)
    #  can_migrate_datasource.update(event)
    cm_events.append(event)


# set up perf buffers
#  b['lb_dst_events'].open_perf_buffer(lb_dst_handler)
#  b['lb_src_events'].open_perf_buffer(lb_src_handler)
#  b['lb_env_events'].open_perf_buffer(lb_env_handler)
b['can_migrate_events'].open_perf_buffer(can_migrate_handler, page_cnt=256)

logger = logging.getLogger('dump')
fhdlr = logging.FileHandler('dump.log')
shdlr = logging.StreamHandler()
logger.addHandler(fhdlr)
logger.addHandler(shdlr)
while True:
    try:
        b.perf_buffer_poll()
        #  print(len(cm_events))
        for event in cm_events:
            can_migrate_datasource.update(event)
        cm_events = []
    except KeyboardInterrupt:
        print(can_migrate_datasource.dump())
        exit()
    except Exception as e:
        logger.warn(e)
