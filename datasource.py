from abc import ABC, abstractmethod
import pandas as pd
import math

from numa_map import cpu_nodemap, NR_NODES

sysctl_migrate_cost = 500000

class DataSource(ABC):

    @abstractmethod
    def update(self, event):
        pass

    @abstractmethod
    def dump(self):
        pass


class CanMigrateData(DataSource):
    def __init__(self, append=False, write_size=1000, write_file):
        self.columns = ['ts', 'curr_pid', 'pid', 'src_cpu', 'dst_cpu', 'imbalance',
                        'src_len', 'src_numa_len', 'src_preferred_len',
                        'delta', 'cpu_idle', 'cpu_not_idle', 'cpu_newly_idle',
                        'same_node', 'prefer_src', 'prefer_dst',
                        'delta_faults', 'total_faults',
                        'dst_len', 'src_load', 'dst_load',
                        'nr_fails', 'cache_nice_tries', 'buddy_hot',
                        'throttled', 'p_running',
                        'test_aggressive',
                        'can_migrate',
                        'pc_0', 'pc_1']
        self.entries = []
        self.write_size = write_size
        self.write_cd = write_size
        self.write_file = write_file
        if not append:
            with open(self.write_file, 'w') as f:
                f.write(','.join(self.columns) + '\n')

    def update(self, event):
        row = {}
        row['ts'] = event.ts
        src_cpu = event.src_cpu
        dst_cpu = event.dst_cpu
        src_nid = cpu_nodemap[src_cpu]
        dst_nid = cpu_nodemap[dst_cpu]
        row['curr_pid'] = event.curr_pid
        row['pid'] = event.pid
        row['src_cpu'] = src_cpu
        row['dst_cpu'] = dst_cpu
        preferred_nid = event.numa_preferred_nid
        row['same_node'] = 1 if src_nid == dst_nid else 0
        row['prefer_src'] = 1 if preferred_nid == src_nid else 0
        row['prefer_dst'] = 1 if preferred_nid == dst_nid else 0
        row['total_faults'] = event.total_numa_faults
        src_faults = event.p_numa_faults[src_nid]
        dst_faults = event.p_numa_faults[dst_nid]
        row['delta_faults'] = dst_faults - src_faults
        row['imbalance'] = event.imbalance
        #  row['delta'] = math.log(event.delta / sysctl_migrate_cost)
        row['delta'] = event.delta
        row['cpu_idle'] = event.cpu_idle
        row['cpu_not_idle'] = event.cpu_not_idle
        row['cpu_newly_idle'] = event.cpu_newly_idle
        row['src_len'] = event.src_nr_running
        row['src_numa_len'] = event.src_nr_numa_running
        row['src_preferred_len'] = event.src_nr_preferred_running
        row['dst_len'] = event.dst_nr_running
        row['src_load'] = event.src_load
        row['dst_load'] = event.dst_load
        row['nr_fails'] = event.nr_balance_failed;
        row['cache_nice_tries'] = event.cache_nice_tries;
        row['buddy_hot'] = event.buddy_hot
        row['p_running'] = event.p_running
        #  row['fair_class'] = event.fair_class
        row['throttled'] = event.throttled
        row['can_migrate'] = event.can_migrate

        row['test_aggressive'] = event.test_aggressive
        row['pc_0'] = event.perf_count_0
        row['pc_1'] = event.perf_count_1
        self.entries.append([str(row[col]) for col in self.columns])
        #  self.df.loc[ts] = row
        self.write_cd -= 1
        if self.write_cd == 0:
            print('.', end=' ', flush=True)
            with open(self.write_file, mode='a') as f:
                for row in self.entries:
                    f.write(','.join(row) + '\n')

            self.write_cd = self.write_size
            self.entries = []

    def dump(self, filename=None):
        filename = filename or self.write_file or 'output.csv'
        with open(self.write_file, mode='a') as f:
            for row in self.entries:
                f.write(','.join(row) + '\n')
        self.entries = []
        return 'Entries Dumped'
