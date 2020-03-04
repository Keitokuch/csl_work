from abc import ABC, abstractmethod
import pandas as pd


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


lb_context = LoadBalanceContext()
