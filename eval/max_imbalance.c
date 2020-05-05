#include <uapi/linux/ptrace.h>
#include <linux/sched.h>

#include "sched.h"


BPF_HISTOGRAM('hist', unsigned int);

int do_perf_event()
{
    unsigned int len = 0;
    pid_t pid = 0;
    struct task_struct *task = NULL;
    struct cfs_rq_partial *my_q = NULL;

    // Fetch the run queue length from task->se.cfs_rq->nr_running. This is an
    // unstable interface and may need maintenance. Perhaps a future version
    // of BPF will support task_rq(p) or something similar as a more reliable
    // interface.
    task = (struct task_struct *)bpf_get_current_task();
    my_q = (struct cfs_rq *)task->se.cfs_rq;
    len = my_q->nr_running;

    // Calculate run queue length by subtracting the currently running task,
    // if present. len 0 == idle, len 1 == one running task.
    if (len > 0)
        len--;

    hist.increment(len);

    return 0;
}

