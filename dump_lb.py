#!/usr/bin/env python3

from bcc import BPF
import sys
import logging
import argparse

from datasource import CanMigrateData

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--tag', help='tag for output')
parser.add_argument('-o', '--output', help='output file name (overwrites -t)')
parser.add_argument('-a', '--append', action='store_true', help='append to output')
parser.add_argument('-s', '--write_size', type=int, action='store')
parser.add_argument('-o', '--old', action='store_true', help='original kernel')
args = parser.parse_args()

write_file = args.output or args.tag and 'raw_' + args.tag or 'output.csv'
write_size = args.write_size or 500

print('Writing to {}'.format(write_file))
cm_events = []
can_migrate_datasource = CanMigrateData(append=args.append,
                                        write_size=write_size,
                                        write_file=write_file)

bpf_text = 'old_dump_lb.c' if args.old or 'dump_lb.c'

# initialize BPF & probes
b = BPF(src_file=bpf_text)


def can_migrate_handler(cpu, data, size):
    event = b['can_migrate_events'].event(data)
    cm_events.append(event)


# set up perf buffers
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
