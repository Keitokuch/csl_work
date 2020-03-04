from abc import ABC, abstractmethod
import pandas as pd

from dump_numa_map import cpu_nodemap

class DataSource(ABC):

    @abstractmethod
    def update(self, event):
        pass

    @abstractmethod
    def poll(self, ts):
        pass

    @abstractmethod
    def dump(self):
        pass


class LoadBalanceContext(DataSource):
    def __init__(self):
        self.df = pd.DataFrame(columns=['ts', 'src_cpu', 'dst_cpu', 'imbalance'])
        self.df.set_index('ts', inplace=True)
        self.na = {'src_cpu': -1, 'dst_cpu': -1, 'imbalance': 'na'}

    def update(self, event):
        ts = event.instance_ts
        src_cpu = event.src_cpu
        dst_cpu = event.dst_cpu
        imbalance = event.imbalance
        self.df.loc[ts] = [src_cpu, dst_cpu, imbalance]

    def poll(self, ts):
        try:
            ret = self.df.loc[ts]
            return ret
        except KeyError:
            print('poll lb_context with invalid index', ts)
            return self.na

    def dump(self):
        return self.df


class CanMigrateData(DataSource):
    def __init__(self):
        columns = ['ts', 'pid', 'src_cpu', 'dst_cpu', 'imbalance',
                   'prefer_src_node', 'prefer_dst_node', 'same_node', 'delta',
                   'delta_faults', 'can_migrate']
        self.df = pd.DataFrame(columns=columns)
        self.df.set_index('ts', inplace=True)

    def update(self, event):
        ts = event.ts
        src_cpu = event.src_cpu
        dst_cpu = event.dst_cpu
        src_nid = cpu_nodemap[src_cpu]
        dst_nid = cpu_nodemap[dst_cpu]
        preferred_nid = event.numa_preferred_nid
        prefer_src = 1 if preferred_nid == src_nid else 0
        prefer_dst = 1 if preferred_nid == dst_nid else 0
        same_node = 1 if src_nid == dst_nid else 0
        src_faults = event.p_numa_faults[src_nid]
        dst_faults = event.p_numa_faults[dst_nid]
        delta_faults = dst_faults - src_faults
        imbalance = event.imbalance
        row = [event.pid, src_cpu, dst_cpu, imbalance,
               prefer_src, prefer_dst, same_node, event.delta,
               delta_faults, event.can_migrate]
        self.df.loc[ts] = row

    def poll(self, ts):
        try:
            ret = self.df.loc[ts]
            return ret
        except KeyError:
            print('poll lb_context with invalid index', ts)
            return self.na

    def dump(self):
        #  return self.df
        self.df.to_csv('output.csv')
        return self.df

#  lb_context = LoadBalanceContext()
can_migrate_datasource = CanMigrateData()
