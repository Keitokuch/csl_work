import psutil

# Iterate over all running process
cpus = {}
while 1:
    for proc in psutil.process_iter():
        try:
            # Get process name & pid from process object.
            processName = proc.name()
            processID = proc.pid
            proc = proc.as_dict()
            status = proc['status']
            cpu_num = proc['cpu_num']
            cpu_list = cpus.get(cpu_num, [])
            cpu_list.append(processID)
            cpu_percent = proc['cpu_percent']
            cpus[cpu_num] = cpu_list
            print(processName , ' ::: ', processID, proc['cpu_num'], status, cpu_percent)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    for c, p in cpus.items():
        print(c, p)
    cpus = {}
