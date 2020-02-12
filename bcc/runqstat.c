#include <uapi/linux/ptrace.h>
#include <linux/sched.h>
#include <linux/pid_namespace.h>
#include <linux/printk.h>

/* BPF_HASH(counts, u64); */
/* BPF_HISTOGRAM(dist, u64); */

/* struct rq { */
/*     unsigned int nr_running; */
/*     int cpu; */
/* }; */

struct rq {
	/* runqueue lock: */
	raw_spinlock_t lock;
	unsigned int nr_running;
};

struct cfs_rq {
	struct load_weight	load;
	unsigned long		runnable_weight;
	unsigned int		nr_running;
	unsigned int		h_nr_running;

	u64			exec_clock;
	u64			min_vruntime;
};

struct data_t {
    unsigned long rw_p;
    unsigned long rw_n;
    unsigned int h_nr_running_p;
    unsigned int h_nr_running_n;
};
BPF_PERF_OUTPUT(events);

int trace_set_task(struct pt_regs *ctx, struct sched_entity *se,
		      struct cfs_rq *prev, struct cfs_rq *next) {
    struct data_t data = {};

    data.rw_p = prev->runnable_weight;
    data.rw_n = next->runnable_weight;

    data.h_nr_running_p = prev->h_nr_running;
    data.h_nr_running_n = next->h_nr_running;

    events.perf_submit(ctx, &data, sizeof(data));

    return 0;
}


/* int trace_enqueue_task(struct pt_regs *ctx, struct rq *rq, struct task_struct *p, int flags) { */
/*     u64 pid, tgid, cpu, jobs; */
/*     u64 *cp, count = 0; */
/*     struct list_head *head, *pos; */
    
/*     [> cpu = prev->cpu; <] */
/*     jobs = rq->nr_running; */

/*     [> struct task_struct *task; <] */
/*     [> pos = (head)->next; <] */
/*     [> void *__mptr = (void *)(pos); <] */
/*     [> task = ((struct task_struct *)(__mptr - offsetof(struct task_struct, se.group_node))); <] */
/*     [> cpu = task->cpu; <] */
/*     dist.increment(jobs); */
/*     [> for (pos = (head)->next; pos != (head); pos = pos->next){ <] */
/*     [> } <] */
/*     [> list_for_each(pos, head){ <] */
/*     [>     struct task_struct *task; <] */
/*     [>     void *__mptr = (void *)(pos); <] */
/*     [>     task = ((struct task_struct *)(__mptr - offsetof(struct task_struct, se.group_node))); <] */
/*     [>     cpu = task->cpu; <] */
/*     [> } <] */

/*     [> dist.increment(cpu);  <] */
/*     [> printk(KERN_INFO "sched cpu %llu\n", cpu); <] */

/*     // cp = counts.lookup(&cpu); */
/*     // if (pid <= 1025) { */
/*         // cp = counts.lookup(&pid); */
/*         // if (cp != 0) { */
/*             // count = *cp + 1; */
/*         // } else { */
/*             // count = 1; */
/*         // } */

/*         // counts.update(&pid, &count); */
/*     // } */

/*     return 0; */
/* } */
