#include <uapi/linux/ptrace.h>
#include <linux/sched.h>
#include <bcc/proto.h>
#include <linux/bpf.h>
#include <linux/kernel.h>
#include <uapi/linux/bpf.h>

#include "sched.h"

#undef offsetof
#define offsetof(TYPE, MEMBER) ((size_t) &((TYPE *)0)->MEMBER)
#undef container_of
#define container_of(ptr, type, member) ({				\
    ((type *)((void *)(ptr) - offsetof(type, member))); })

#define NR_PIDS 10
#define TASK_RUNNING			0x0000

// #define EQ_FN enqueue_task_fair
// #define DQ_FN dequeue_task_fair
#define EQ_FN activate_task
#define DQ_FN deactivate_task

#define KPROBE(fn)  _KPROBE(fn)
#define _KPROBE(fn) kprobe__##fn
#define KRETPROBE(fn)  _KRETPROBE(fn)
#define _KRETPROBE(fn) kretprobe__##fn

struct cs_data {
    u64 ts;
    int cpu;
    int p_pid;
    int n_pid;
    long prev_state;
    char comm[TASK_COMM_LEN];
    unsigned int len;
    int curr_pid;
    unsigned long runnable_weight;
    int pid_cnt;
    int pids[NR_PIDS];
    unsigned long weights[NR_PIDS];
};

struct tsk_data {
    u64 ts;
    int cpu;
    int pid;
    int tgid;
    char comm[TASK_COMM_LEN];
    int prio;
    char oldcomm[TASK_COMM_LEN];
};

struct rq_data {
    u64 ts;
    // int enqueue;
    int qc_pid;
    int qc_cpu;
    int qc_flags;

    int curr_pid;
    char comm[TASK_COMM_LEN];
    unsigned int len;
    unsigned long runnable_weight;
    int pid_cnt;
    int pids[NR_PIDS];
    long states[NR_PIDS];
    /* long states[NR_PIDS]; */
    unsigned long weights[NR_PIDS];
};

struct lb_data {
    u64 ts;
    /* int cpu; */
    int dst_cpu;
    int src_cpu;
    int pid;
    char comm[TASK_COMM_LEN];
    int nr_jobs;
};

struct rq_change {
    struct rq *rq;
    struct task_struct *p;
    int flags;
};

BPF_HASH(cpu_eq, int, struct rq_change);
BPF_HASH(cpu_dq, int, struct rq_change);

BPF_PERF_OUTPUT(cs_events);
BPF_PERF_OUTPUT(lb_events);
BPF_PERF_OUTPUT(dq_events);
BPF_PERF_OUTPUT(eq_events);
BPF_PERF_OUTPUT(tn_events);
BPF_PERF_OUTPUT(td_events);
/* BPF_PERF_OUTPUT(te_events); */
BPF_PERF_OUTPUT(rq_events);
BPF_PERF_OUTPUT(rn_events);
BPF_PERF_OUTPUT(yield_events);


TRACEPOINT_PROBE(sched, sched_switch) {

    struct cs_data data = {};
    char comm[TASK_COMM_LEN];
    struct task_struct *task;
    struct cfs_rq *cfs;
    struct rq *rq;
    struct list_head *head, *pos;

    bpf_probe_read_str(&(data.comm), sizeof(comm), args->next_comm);
    data.ts = bpf_ktime_get_ns();
    data.p_pid = args->prev_pid;
    data.n_pid = args->next_pid;
    data.prev_state = args->prev_state;

    task = (struct task_struct *)bpf_get_current_task();
    data.curr_pid = task->pid;
    cfs = (struct cfs_rq *)task->se.cfs_rq;
    rq = cfs->rq;

    data.len = cfs->h_nr_running;
    data.runnable_weight = cfs->runnable_weight;
    head = &(rq->cfs_tasks);
    pos = head;
    int i;
    int cnt;
    cnt = 0;
    data.pid_cnt = 0;
    for (i = 0; i < NR_PIDS; i++) {
        pos = pos->next;
        if (pos == head)
            break;
        task = container_of(pos, struct task_struct, se.group_node);
        data.pids[i] = task->pid;
        data.weights[i] = task->se.runnable_weight;
    }
    data.pid_cnt = i;

    cs_events.perf_submit(args, &data, sizeof(data));
    return 0;
}

int KPROBE(EQ_FN)(struct pt_regs *ctx, struct rq *rq, struct task_struct *p, int flags)
{
    int cpu = bpf_get_smp_processor_id();
    struct rq_change qc = {};

    qc.flags = flags;
    qc.rq = rq;
    qc.p = p;

    cpu_eq.update(&cpu, &qc);
    return 0;
}

int KPROBE(DQ_FN)(struct pt_regs *ctx, struct rq *rq, struct task_struct *p, int flags)
{
    int cpu = bpf_get_smp_processor_id();
    struct rq_change qc = {};

    qc.flags = flags;
    qc.rq = rq;
    qc.p = p;

    cpu_dq.update(&cpu, &qc);
    return 0;
}

int KRETPROBE(EQ_FN)(struct pt_regs *ctx)
{
    struct rq_data data = {};
    struct task_struct *curr_task, *p;
    struct cfs_rq *cfs;
    struct rq *rq;
    struct rq_change *qc;
    int cpu = bpf_get_smp_processor_id();
    // task = (struct task_struct *)bpf_get_current_task();
    
    data.ts = bpf_ktime_get_ns();
    // cfs = (struct cfs_rq *)task->se.cfs_rq;
    // rq = cfs->rq;

    qc = (struct rq_change *)cpu_eq.lookup(&cpu);
    if (!qc)
        return 0;
    rq = qc->rq;
    p = qc->p;
    data.qc_flags = qc->flags;

    cfs = &rq->cfs;
    curr_task = rq->curr;
    data.curr_pid = curr_task->pid;
    bpf_probe_read_str(&(data.comm), sizeof(data.comm), curr_task->comm);
    data.qc_pid = p->pid;
    data.qc_cpu = rq->cpu;
    data.len = cfs->h_nr_running;
    data.runnable_weight = cfs->runnable_weight;
    data.pid_cnt = 0;

    struct list_head *head, *pos;
    int i;
    struct task_struct *task;
    // int cnt = 0;

    head = &(rq->cfs_tasks);
    pos = head;
    for (i = 0; i < NR_PIDS; i++) {
        pos = pos->next;
        if (pos == head)
            break;
        task = container_of(pos, struct task_struct, se.group_node);
        data.pids[i] = task->pid;
        data.weights[i] = task->se.runnable_weight;
    }
    data.pid_cnt = i;

    eq_events.perf_submit(ctx, &data, sizeof(data));
    return 0;
}

int KRETPROBE(DQ_FN)(struct pt_regs *ctx)
{
    struct rq_data data = {};
    struct task_struct *curr_task, *p;
    struct cfs_rq *cfs;
    struct rq *rq;
    struct rq_change *qc;
    int cpu = bpf_get_smp_processor_id();
    
    data.ts = bpf_ktime_get_ns();

    qc = (struct rq_change *)cpu_eq.lookup(&cpu);
    if (!qc)
        return 0;
    rq = qc->rq;
    p = qc->p;
    data.qc_flags = qc->flags;

    cfs = &rq->cfs;
    curr_task = rq->curr;
    data.curr_pid = curr_task->pid;
    bpf_probe_read_str(&(data.comm), sizeof(data.comm), curr_task->comm);
    data.qc_pid = p->pid;
    data.qc_cpu = rq->cpu;
    data.len = cfs->h_nr_running;
    data.runnable_weight = cfs->runnable_weight;
    data.pid_cnt = 0;

    struct list_head *head, *pos;
    int i;
    struct task_struct *task;

    head = &(rq->cfs_tasks);
    pos = head;
    for (i = 0; i < NR_PIDS; i++) {
        pos = pos->next;
        if (pos == head)
            break;
        task = container_of(pos, struct task_struct, se.group_node);
        data.pids[i] = task->pid;
        // data.states[i] = task->state;
        data.weights[i] = task->se.runnable_weight;
    }
    data.pid_cnt = i;

    dq_events.perf_submit(ctx, &data, sizeof(data));
    return 0;
}

/*
int trace_rq(struct pt_regs *ctx)
{
    struct rq_data data = {};
    struct task_struct *task;
    struct cfs_rq *cfs;
    struct rq *rq;
    struct list_head *head, *pos;
    struct rq_change *qc;
    int cpu = bpf_get_smp_processor_id();
    
    data.ts = bpf_ktime_get_ns();
    task = (struct task_struct *)bpf_get_current_task();
    bpf_probe_read_str(&(data.comm), sizeof(data.comm), task->comm);
    data.curr_pid = task->pid;
    cfs = (struct cfs_rq *)task->se.cfs_rq;
    rq = cfs->rq;

    qc = (struct rq_change *)cpu_qc.lookup(&cpu);
    if (!qc)
        return 0;
    data.qc_pid = qc->pid;
    data.enqueue = qc->enqueue;

    data.len = cfs->h_nr_running;
    data.runnable_weight = cfs->runnable_weight;
    head = &(rq->cfs_tasks);
    pos = head;
    int i;
    int cnt;
    cnt = 0;
    data.pid_cnt = 0;
    for (i = 0; i < NR_PIDS; i++) {
        pos = pos->next;
        if (pos == head)
            break;
        task = container_of(pos, struct task_struct, se.group_node);
        data.pids[i] = task->pid;
        data.weights[i] = task->se.runnable_weight;
    }
    data.pid_cnt = i;

    rq_events.perf_submit(ctx, &data, sizeof(data));
    return 0;
}
*/

/*
int trace_new_task(struct pt_regs *ctx, struct task_struct *p)
{
    struct eq_data data = {};
    
    // data.ts = bpf_ktime_get_ns();
    data.ts = 1;
    data.pid = p->pid;
    bpf_probe_read_str(&(data.comm), sizeof(p->comm), p->comm);

    tn_events.perf_submit(ctx, &data, sizeof(data));
    return 0;
}
*/

TRACEPOINT_PROBE(sched, sched_wakeup_new) {

    struct tsk_data data = {};
    data.ts = bpf_ktime_get_ns();
    data.pid = args->pid;
    data.prio = args->prio;
    data.cpu = args->target_cpu;
    bpf_probe_read_str(&(data.comm), sizeof(args->comm), args->comm);
    tn_events.perf_submit(args, &data, sizeof(data));
    return 0;
}

TRACEPOINT_PROBE(task, task_rename) {
    struct tsk_data data = {};
    data.ts = bpf_ktime_get_ns();
    data.pid = args->pid;
    bpf_probe_read_str(&(data.oldcomm), sizeof(args->oldcomm), args->oldcomm);
    bpf_probe_read_str(&(data.comm), sizeof(args->newcomm), args->newcomm);
    rn_events.perf_submit(args, &data, sizeof(data));
    return 0;
}

int kprobe__do_task_dead(struct pt_regs *ctx)
{
    struct tsk_data data = {};
    struct task_struct *p;
    
    data.ts = bpf_ktime_get_ns();
    p = (struct task_struct *)bpf_get_current_task();
    data.pid = p->pid;
    data.prio = p->prio;
    bpf_probe_read_str(&(data.comm), sizeof(p->comm), p->comm);

    td_events.perf_submit(ctx, &data, sizeof(data));
    return 0;
}


// set_task_cpu also records new task setting first cpu;
// So not using
int kprobe__set_task_cpu(struct pt_regs *ctx, struct task_struct *p, unsigned int new_cpu)
{
    struct lb_data data = {};
    
    data.ts = bpf_ktime_get_ns();
    data.dst_cpu = new_cpu;
    data.pid = p->pid;
    data.src_cpu = p->cpu;
    data.nr_jobs = p->se.cfs_rq->h_nr_running;
    bpf_probe_read_str(&(data.comm), sizeof(data.comm), p->comm);

    lb_events.perf_submit(ctx, &data, sizeof(data));
    return 0;
}

// Loses records of itself
/*
TRACEPOINT_PROBE(sched, sched_migrate_task) {
    struct lb_data data = {};
    data.ts = bpf_ktime_get_ns();
    data.ts = 0;
    data.pid = args->pid;
    
    data.src_cpu = args->orig_cpu;
    data.dst_cpu = args->dest_cpu;
    bpf_probe_read_str(&(data.comm), sizeof(args->comm), args->comm);

    lb_events.perf_submit(args, &data, sizeof(data));
    return 0;
}
*/



// int PROBE(yield_task_fair)(struct pt_regs *ctx, struct rq *rq) {
    // struct cs_data data = {};
    // data.ts = bpf_ktime_get_ns();
    // data.cpu = rq->cpu;
    // data.curr_pid = rq->curr->pid;

    // yield_events.perf_submit(ctx, &data, sizeof(data));
    // return 0;
// }

/*
int kprobe__finish_task_switch(struct pt_regs *ctx, struct task_struct *prev)
{
    struct cs_data data = {};
    struct task_struct *curr;

    char comm[TASK_COMM_LEN];
    bpf_get_current_comm(&(data.comm), sizeof(comm));

    data.ts = bpf_ktime_get_ns();
    data.ts = 1;
    // data.cpu = bpf_get_smp_processor_id();
    curr = (struct task_struct *)bpf_get_current_task();
    data.p_pid = prev->pid;
    data.n_pid = curr->pid;

    cs_events.perf_submit(ctx, &data, sizeof(data));

    return 0;
}
*/
