import warnings


class Scheduler():
    def __init__(self, nr_cpu=8):
        self.nr_cpu = nr_cpu
        self.tasks = Tasks()
        self.runqueues = RunQueues(nr_cpu)

    def update(self, update_event):
        event_type, data = update_event[0], update_event[1:]
        if event_type == 'new':
            self.tasks.new(data)
        elif event_type == 'tsk':
            self.tasks.ensure(data)
        elif event_type == 'dead':
            self.tasks.dead(data)
        elif event_type == 'eq':
            self.runqueues.enqueue(data)
            self.tasks.ensure(data)
        elif event_type == 'dq':
            self.runqueues.dequeue(data)
        elif event_type == 'rq':
            self.runqueues.ensure(data)
        elif event_type == 'rn':
            self.tasks.rename(data)


class Migration():
    def __init__(self, pid, src_cpu, dst_cpu):
        self.pid = pid
        self.src_cpu = src_cpu
        self.dst_cpu = dst_cpu


class RunQueue():
    def __init__(self, cpu):
        self.cpu = cpu
        self.cfs_tasks = []
        self.runnable_weight = 0
        self.nr_running = 0
        self.ensured = False

    def __repr__(self):
        return f'{self.cpu} {self.cfs_tasks}'

    def enqueue(self, pid):
        if pid in self.cfs_tasks:
            #  raise Exception(f"Eq PID {pid} already in rq{self.cpu} {self.cfs_tasks}")
            print(f"Eq PID {pid} already in rq{self.cpu} {self.cfs_tasks}")
            global possible_faults
            possible_faults['eq'] += 1
        else:
            self.cfs_tasks.append(pid)
            self.nr_running += 1
        #  print('eq', pid, self.cpu, self.cfs_tasks)

    def dequeue(self, pid):
        try:
            self.cfs_tasks.remove(pid)
            self.nr_running -= 1
        except ValueError:
            if self.ensured:
                global possible_faults
                possible_faults['dq'] += 1
                print(f'Dequeuing invalid task {pid} from {self.cfs_tasks} cpu{self.cpu}')
        #  print('dq', pid, self.cpu, self.cfs_tasks)

    def ensure(self, pids, weight, nr_running):
        self.cfs_tasks = pids
        self.runnable_weight = weight
        self.nr_running = nr_running
        self.ensured = True
        print(self.cpu, self.cfs_tasks)



class Task(object):
    def __init__(self, pid, comm, weight=0):
        self.pid = pid
        self.comm = comm
        self.weight = weight

    def __str__(self):
        return f'{self.pid} {self.comm}'

    def __repr__(self):
        return f'{self.pid} {self.comm}'


class RunQueues():
    def __init__(self, nr_cpu):
        self.rqs = [RunQueue(cpu) for cpu in range(nr_cpu)]

    def __repr__(self):
        return str(self.rqs)

    def enqueue(self, data):
        pid, cpu, qc, _, _ = data
        if qc == 0:
            raise Exception('Dequeue NO QChange')
        self.rqs[cpu].enqueue(pid)

    def dequeue(self, data):
        pid, cpu, qc = data
        if qc == 0:
            raise Exception('Dequeue NO QChange')
        self.rqs[cpu].dequeue(pid)

    def ensure(self, data):
        cpu, pids, weight, nr_running = data
        self.rqs[cpu].ensure(pids, weight, nr_running)


class Tasks():
    def __init__(self):
        self.tasks = {}

    def __repr__(self):
        return str(self.tasks)

    def new(self, data):
        pid, comm = data
        if pid in self.tasks:
            raise Exception(f'new task {comm} with existing PID {pid} {self.tasks[pid].comm}')
        else:
            self.tasks[pid] = Task(pid, comm)

    def dead(self, data):
        pid, comm = data
        if pid in self.tasks:
            if self.tasks[pid].comm != comm:
                raise Exception('Dead task with wrong COMM')
            del self.tasks[pid]
        else:
            print('Unseen task dead!')

    def ensure(self, data):
        pid, _, _, comm, weight = data
        if pid not in self.tasks:
            #  print(f'waking unseen task {pid} {comm}')
            #  print(self.tasks)
            self.tasks[pid] = Task(pid, comm, weight)
        else:
            if self.tasks[pid].comm != comm:
                print('tsk change comm')
                self.tasks[pid].comm = comm
            elif self.tasks[pid].weight != weight:
                #  print(f'tsk {pid} change weight from {self.tasks[pid].weight} to {weight}')
                self.tasks[pid].weight = weight
            #  else:
                #  print(f'ENSURING NOTHING! for task {pid}')

    def rename(self, data):
        pid, comm = data
        if pid not in self.tasks:
            print('Renaming unseen task, creating instead')
            self.new((pid, comm))
        else:
            #  print(f'rename {pid} from {self.tasks[pid].comm} to {comm}')
            self.tasks[pid].comm = comm


possible_faults = {'eq': 0, 'dq': 0}
NR_CPU = 8
scheduler = Scheduler(NR_CPU)
