#include <uapi/linux/ptrace.h>
#include <linux/sched.h>

#include "sched.h"

#undef offsetof
#define offsetof(TYPE, MEMBER) ((size_t) &((TYPE *)0)->MEMBER)
#undef container_of
#define container_of(ptr, type, member) ({				\
    ((type *)((void *)(ptr) - offsetof(type, member))); })


struct cs_data {
    u64 ts;
    int cpu;
    unsigned int p_pid;
    unsigned int n_pid;
};

struct eq_data {
    u64 ts;
    int cpu;
    int pid;
    int tgid;
};

struct rq_data {
    u64 ts;
    /* int cpu; */
    /* unsigned int h_len; */
    unsigned int len;
    unsigned long runnable_weight;
    /* unsigned long weight; */
};

/* struct cfs_rq { */
/*     struct load_weight	load; */
/*     unsigned long		runnable_weight; */
/*     unsigned int		nr_running; */
/*     unsigned int		h_nr_running; */

/*     u64			exec_clock; */
/*     u64			min_vruntime; */

/*     struct rb_root_cached tasks_timeline; */
/* }; */

/* struct rq_flags {}; */

BPF_PERF_OUTPUT(cs_events);
/* BPF_PERF_OUTPUT(lb_events); */
BPF_PERF_OUTPUT(dq_events);
BPF_PERF_OUTPUT(eq_events);
BPF_PERF_OUTPUT(tn_events);
BPF_PERF_OUTPUT(td_events);
/* BPF_PERF_OUTPUT(te_events); */
BPF_PERF_OUTPUT(rq_events);

/* BPF_HISTOGRAM(dist, unsigned int); */

/* int trace_context_switch(struct pt_regs *ctx, struct rq *rq, struct task_struct *prev,  */
/*                         struct task_struct *next)  */
int trace_context_switch(struct pt_regs *ctx, struct task_struct *prev)
{
    struct cs_data data = {};
    struct task_struct *curr;

    data.ts = bpf_ktime_get_ns();
    /* data.cpu = bpf_get_smp_processor_id(); */
    curr = (struct task_struct *)bpf_get_current_task();
    data.p_pid = prev->pid;
    data.n_pid = curr->pid;

    cs_events.perf_submit(ctx, &data, sizeof(data));

    return 0;
}

int trace_enqueue_task(struct pt_regs *ctx, struct rq *rq, struct task_struct *p, int flags)
{
    struct eq_data data = {};
    struct task_struct *task;

    data.ts = bpf_ktime_get_ns();
    data.cpu = rq->cpu;
    data.pid = p->pid;
    data.tgid = p->tgid;

    eq_events.perf_submit(ctx, &data, sizeof(data));
    return 0;
}

int trace_dequeue_task(struct pt_regs *ctx, struct rq *rq, struct task_struct *p, int flags)
{
    struct eq_data data = {};

    data.ts = bpf_ktime_get_ns();
    data.cpu = rq->cpu;
    data.pid = p->pid;
    data.tgid = p->tgid;

    dq_events.perf_submit(ctx, &data, sizeof(data));
    return 0;
}

int trace_new_task(struct pt_regs *ctx, struct task_struct *p)
{
    struct eq_data data = {};
    
    data.ts = bpf_ktime_get_ns();
    data.pid = p->pid;
    data.tgid = p->tgid;

    tn_events.perf_submit(ctx, &data, sizeof(data));
    return 0;
}

int trace_dead(struct pt_regs *ctx)
{
    struct eq_data data = {};
    struct task_struct *p;
    
    data.ts = bpf_ktime_get_ns();
    p = (struct task_struct *)bpf_get_current_task();
    data.pid = p->pid;
    data.tgid = p->tgid;

    td_events.perf_submit(ctx, &data, sizeof(data));
    return 0;
}

/*
int trace_exit(struct pt_regs *ctx, struct task_struct *p)
{
    struct eq_data data = {};
    
    data.ts = bpf_ktime_get_ns();
    data.pid = p->pid;
    data.tgid = p->tgid;

    te_events.perf_submit(ctx, &data, sizeof(data));
    return 0;
}
*/

int trace_rq(struct pt_regs *ctx)
{
    struct rq_data data = {};
    struct task_struct *task;
    struct cfs_rq *cfs;
    
    data.ts = bpf_ktime_get_ns();
    task = (struct task_struct *)bpf_get_current_task();
    cfs = (struct cfs_rq *)task->se.cfs_rq;
    data.len = cfs->h_nr_running;
    /* data.len = cfs->nr_running; */
    data.runnable_weight = cfs->runnable_weight;
    /* data.weight = cfs->load.weight; */

    rq_events.perf_submit(ctx, &data, sizeof(data));
    return 0;
}
