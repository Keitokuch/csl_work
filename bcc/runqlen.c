#include <uapi/linux/ptrace.h>
#include <linux/sched.h>
#include <linux/rbtree_augmented.h>
// Declare enough of cfs_rq to find nr_running, since we can't #import the
// header. This will need maintenance. It is from kernel/sched/sched.h:
#undef offsetof
#define offsetof(TYPE, MEMBER) ((size_t) &((TYPE *)0)->MEMBER)
#undef container_of
#define container_of(ptr, type, member) ({				\
    ((type *)((void *)(ptr) - offsetof(type, member))); })

struct data_t {
    int cpu;
    unsigned int h_nr_running;
    unsigned long runnable_weight;
    unsigned long weight;
    unsigned int pid;
};

struct cfs_rq {
	struct load_weight	load;
	unsigned long		runnable_weight;
	unsigned int		nr_running;
	unsigned int		h_nr_running;

	u64			exec_clock;
	u64			min_vruntime;

    struct rb_root_cached tasks_timeline;
};

BPF_PERF_OUTPUT(events);
BPF_HISTOGRAM(dist, unsigned int);

int do_perf_event(struct pt_regs *ctx)
{
    unsigned int len = 0;
    pid_t pid = 0;
    struct task_struct *task;
    struct cfs_rq *my_q;
    struct sched_entity *se;
    struct data_t data = {};

    task = (struct task_struct *)bpf_get_current_task();
    my_q = (struct cfs_rq *)task->se.cfs_rq;

    struct rb_node *left = my_q->tasks_timeline.rb_leftmost;

    len = my_q->h_nr_running; 
    /* struct sched_entity *kse = container_of(left, struct sched_entity, run_node); */
    /* struct task_struct *ktask = container_of(se, struct task_struct, se); */
    /* int i; */
    /* for (i = 0; i < 99; i++) */
    /*     if (left) { */
    /*         se = container_of(left, struct sched_entity, run_node); */
    /*         task = container_of(se, struct task_struct, se); */
    /*     } */

    if (left) {
        se = container_of(left, struct sched_entity, run_node);
        task = container_of(se, struct task_struct, se);
    }

    /* task = ktask; */
    /* se = kse; */

    /* bpf_probe_read(task, 8, (void *)ktask); */
    // Fetch the run queue length from task->se.cfs_rq->nr_running. This is an
    // unstable interface and may need maintenance. Perhaps a future version
    // of BPF will support task_rq(p) or something similar as a more reliable
    // interface.

    data.cpu = task->cpu;
    data.pid = task->pid;
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
