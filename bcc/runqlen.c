#include <uapi/linux/ptrace.h>
#include <linux/sched.h>
// Declare enough of cfs_rq to find nr_running, since we can't #import the
// header. This will need maintenance. It is from kernel/sched/sched.h:

struct data_t {
    int cpu;
    unsigned int h_nr_running;
    unsigned long runnable_weight;
    unsigned long weight;
};

struct cfs_rq {
	struct load_weight	load;
	unsigned long		runnable_weight;
	unsigned int		nr_running;
	unsigned int		h_nr_running;

	u64			exec_clock;
	u64			min_vruntime;
};

BPF_PERF_OUTPUT(events);
BPF_HISTOGRAM(dist, unsigned int);

int do_perf_event(struct pt_regs *ctx)
{
    unsigned int len = 0;
    pid_t pid = 0;
    struct task_struct *task = NULL;
    struct cfs_rq *my_q = NULL;
    struct data_t data = {};
    // Fetch the run queue length from task->se.cfs_rq->nr_running. This is an
    // unstable interface and may need maintenance. Perhaps a future version
    // of BPF will support task_rq(p) or something similar as a more reliable
    // interface.
    task = (struct task_struct *)bpf_get_current_task();
    my_q = (struct cfs_rq *)task->se.cfs_rq;
    data.cpu = task->cpu;
    data.h_nr_running = my_q->h_nr_running;
    data.runnable_weight = my_q->runnable_weight;
    data.weight = my_q->load.weight;
    // Calculate run queue length by subtracting the currently running task,
    // if present. len 0 == idle, len 1 == one running task.
    /* if (len > 0) */
    /*     len--; */
    /* dist.increment(len); */
    events.perf_submit(ctx, &data, sizeof(data));
    return 0;
}
