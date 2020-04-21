#!/usr/bin/env python3

from bcc import BPF
import sys
import logging

from datasource import CanMigrateData


cm_events = []
can_migrate_datasource = CanMigrateData(append=False, write_size=800,
                                        write_file='./test0.csv')

# initialize BPF & probes
b = BPF(src_file='dump_lb.c')


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
