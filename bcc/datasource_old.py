from abc import ABC, abstractmethod
import pandas as pd


class DataSource(ABC):

    @abstractmethod
    def update(self, event):
        pass

    @abstractmethod
    def poll(self, ts, env):
        pass


class Scheduler(DataSource):
    def __init__(self, nr_cpu):
        self.tasks = Tasks()
        self.runqueues = RunQueues(nr_cpu)

    def update(self, event):
        print(event.runnable_weight)
        #  event_type = event.type
        #  if event_type == 'new':
            #  self.tasks.update(event)

    def poll(self, ts, env):
        self.tasks.poll(ts)
        self.runqueues.poll(ts)


class RunQueues(DataSource):
    def __init__(self, nr_cpu):
        self.rqs = [RunQueue(cpu) for cpu in range(nr_cpu)]

    def __repr__(self):
        return str(self.rqs)

    def update(self, event):
        pass

    def poll(self, ts, env):
        pass


class Tasks(DataSource):
    def __init__(self):
        self.tasks = {}
        self.df = pd.DataFrame(columns=['ts', 'type', 'pid', 'comm', 'weight'])

    def update(self, event):
        pass

    def poll(self, ts, env):
        pass


class RunQueue(DataSource):
    def __init__(self, cpu):
        self.cpu = cpu
        self.cfs_tasks = []
        self.runnable_weight = 0
        self.nr_running = 0
        self.ensured = False

    def update(self, event):
        pass

    def poll(self, ts, env):
        pass


class Task(DataSource):
    def __init__(self, pid, comm, weight=0):
        self.pid = pid
        self.comm = comm
        self.weight = weight

    def update(self, event):
        pass

    def poll(self, ts, env):
        pass


NR_CPU = 8
scheduler = Scheduler(NR_CPU)
