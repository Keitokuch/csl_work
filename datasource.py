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
    def __init__(self, autowrite=False, write_size=1000, write_file=None):
        columns = ['ts', 'pid', 'src_cpu', 'dst_cpu', 'imbalance',
                   'prefer_src', 'prefer_dst', 'same_node', 'delta',
                   'delta_faults', 'can_migrate', 'fault0', 'fault1', 'prefer_nid']
        self.df = pd.DataFrame(columns=columns)
        self.df.set_index('ts', inplace=True)
        self.autowrite = autowrite
        if autowrite:
            if not write_file:
                raise ValueError('write_file has to be specified for autowrite')
            self.write_size = write_size
            self.write_cd = write_size
            self.write_file = write_file
            self.df.to_csv(self.write_file)


    def update(self, event):
        row = {}
        ts = event.ts
        src_cpu = event.src_cpu
        dst_cpu = event.dst_cpu
        src_nid = cpu_nodemap[src_cpu]
        dst_nid = cpu_nodemap[dst_cpu]
        row['pid'] = event.pid
        row['src_cpu'] = src_cpu
        row['dst_cpu'] = dst_cpu
        preferred_nid = event.numa_preferred_nid
        row['prefer_nid'] = preferred_nid
        row['fault0'] = event.p_numa_faults[0]
        row['fault1'] = event.p_numa_faults[1]
        row['prefer_src'] = 1 if preferred_nid == src_nid else 0
        row['prefer_dst'] = 1 if preferred_nid == dst_nid else 0
        row['same_node'] = 1 if src_nid == dst_nid else 0
        src_faults = event.p_numa_faults[src_nid]
        dst_faults = event.p_numa_faults[dst_nid]
        #  print(event.)
        row['delta_faults'] = dst_faults - src_faults
        row['imbalance'] = event.imbalance
        row['delta'] = event.delta
        row['can_migrate'] = event.can_migrate
        self.df.loc[ts] = row
        if self.autowrite:
            self.write_cd -= 1
            if self.write_cd == 0:
                self.df.to_csv(self.write_file, mode='a', header=False)
                self.write_cd = self.write_size
                self.df = self.df.iloc[:0]

    def poll(self, ts):
        try:
            ret = self.df.loc[ts]
            return ret
        except KeyError:
            print('poll lb_context with invalid index', ts)
            return self.na

    def dump(self, filename=None):
        #  return self.df
        filename = filename or self.write_file or 'output.csv'
        if not self.autowrite:
            self.df.to_csv(filename)
        else:
            self.df.to_csv(self.write_file, mode='a', header=False)
        return self.df

#  lb_context = LoadBalanceContext()
can_migrate_datasource = CanMigrateData(autowrite=True, write_size=300, write_file='cmdata.csv')
