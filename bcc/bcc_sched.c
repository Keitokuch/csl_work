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

#define NR_PIDS 7
#define TASK_RUNNING			0x0000

#define EQ_FN enqueue_task_fair
#define DQ_FN dequeue_task_fair

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
    char comm[TASK_COMM_LEN];
    int prio;
    unsigned long runnable_weight;
    char oldcomm[TASK_COMM_LEN];
};

struct qc_data {
    u64 ts;
    int pid;
    int cpu;
    int flags;
    int qc;
    char comm[TASK_COMM_LEN];
    unsigned long runnable_weight;
};

struct rq_data {
    u64 ts;
    int cpu;
    int curr_pid;
    char comm[TASK_COMM_LEN];
    unsigned int len;
    unsigned long runnable_weight;
    int pid_cnt;
    int pids[NR_PIDS];
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
    long imbalance;
    int degrades_locality;
};

struct rq_change {
    struct rq *rq;
    struct task_struct *p;
    int prev_len;
    int flags;
};

struct lb_param {
    struct task_struct *p;
    struct lb_env *env;
};

BPF_HASH(cpu_eq, int, struct rq_change);
BPF_HASH(cpu_dq, int, struct rq_change);
BPF_HASH(lb_migrate, int, struct lb_param);

BPF_PERF_OUTPUT(dq_events);
BPF_PERF_OUTPUT(eq_events);
BPF_PERF_OUTPUT(rq_events);
BPF_PERF_OUTPUT(tn_events);
BPF_PERF_OUTPUT(td_events);
/* BPF_PERF_OUTPUT(tsk_events); */
BPF_PERF_OUTPUT(rn_events);
/* BPF_PERF_OUTPUT(locality_events); */


static void dump_rq(struct rq_data *data, struct rq *rq, struct task_struct *p) {

    struct cfs_rq *cfs;
    struct task_struct *curr_task;
    struct list_head *head, *pos;
    int i;
    struct task_struct *task;

    cfs = &rq->cfs;
    curr_task = rq->curr;
    data->curr_pid = curr_task->pid;
    data->cpu = rq->cpu;
    bpf_probe_read_str(&(data->comm), sizeof(data->comm), curr_task->comm);
    data->len = cfs->h_nr_running;
    data->runnable_weight = cfs->runnable_weight;
    data->pid_cnt = 0;

    head = &(rq->cfs_tasks);
    pos = head;
    /*
    for (i = 0; i < NR_PIDS; i++) {
        pos = pos->next;
        if (pos == head)
            break;
        task = container_of(pos, struct task_struct, se.group_node);
        data->pids[i] = task->pid;
        data->weights[i] = task->se.runnable_weight;
    }
    data->pid_cnt = i;
    */
    int j = 0;
    for (i = 0; i < NR_PIDS; i++) {
        pos = pos->next;
        if (pos == head)
            break;
        task = container_of(pos, struct task_struct, se.group_node);
        data->pids[j] = task->pid;
        j++;
        pos = pos->next;
        if (pos == head)
            break;
        task = container_of(pos, struct task_struct, se.group_node);
        data->pids[j] = task->pid;
        j++;
    }
    data->pid_cnt = j;
}


int KPROBE(EQ_FN)(struct pt_regs *ctx, struct rq *rq, struct task_struct *p, int flags)
{
    int cpu = bpf_get_smp_processor_id();
    struct rq_change qc = {};

    qc.flags = flags;
    qc.rq = rq;
    qc.p = p;
    qc.prev_len = rq->cfs.h_nr_running;

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
    qc.prev_len = rq->cfs.h_nr_running;

    cpu_dq.update(&cpu, &qc);

    return 0;
}

int KRETPROBE(EQ_FN)(struct pt_regs *ctx)
{
    struct qc_data data = {};
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

    data.flags = qc->flags;
    data.qc = rq->cfs.h_nr_running - qc->prev_len;
    data.pid = p->pid;
    data.cpu = rq->cpu;

    bpf_probe_read_str(&(data.comm), sizeof(data.comm), p->comm);
    data.runnable_weight = p->se.runnable_weight;

    eq_events.perf_submit(ctx, &data, sizeof(data));

    struct rq_data rq_data = {};
    rq_data.ts = data.ts;
    dump_rq(&rq_data, rq, p);
    rq_events.perf_submit(ctx, &rq_data, sizeof(rq_data));

    /* struct tsk_data tsk_data = {}; */
    /* tsk_data.ts = bpf_ktime_get_ns(); */
    /* tsk_data.pid = p->pid; */
    /* bpf_probe_read_str(&(tsk_data.comm), sizeof(tsk_data.comm), p->comm); */
    /* tsk_data.runnable_weight = p->se.runnable_weight; */
    /* tsk_events.perf_submit(ctx, &tsk_data, sizeof(tsk_data)); */

    return 0;
}

int KRETPROBE(DQ_FN)(struct pt_regs *ctx)
{
    struct qc_data data = {};
    struct task_struct *curr_task, *p;
    struct cfs_rq *cfs;
    struct rq *rq;
    struct rq_change *qc;
    int delta_task;
    int cpu = bpf_get_smp_processor_id();
    
    data.ts = bpf_ktime_get_ns();

    qc = (struct rq_change *)cpu_dq.lookup(&cpu);
    if (!qc)
        return 0;
    rq = qc->rq;
    p = qc->p;

    data.flags = qc->flags;
    data.qc = rq->cfs.h_nr_running - qc->prev_len;
    data.pid = p->pid;
    data.cpu = rq->cpu;

    bpf_probe_read_str(&(data.comm), sizeof(data.comm), p->comm);
    data.runnable_weight = p->se.runnable_weight;

    dq_events.perf_submit(ctx, &data, sizeof(data));

    struct rq_data rq_data = {};
    rq_data.ts = data.ts;
    dump_rq(&rq_data, rq, p);
    rq_events.perf_submit(ctx, &rq_data, sizeof(rq_data));

    /* struct tsk_data tsk_data = {}; */
    /* tsk_data.ts = bpf_ktime_get_ns(); */
    /* tsk_data.pid = p->pid; */
    /* bpf_probe_read_str(&(tsk_data.comm), sizeof(tsk_data.comm), p->comm); */
    /* tsk_data.runnable_weight = p->se.runnable_weight; */
    /* tsk_events.perf_submit(ctx, &tsk_data, sizeof(tsk_data)); */

    return 0;
}

TRACEPOINT_PROBE(sched, sched_process_fork) {
    struct tsk_data data = {};
    data.ts = bpf_ktime_get_ns();
    data.pid = args->child_pid;
    bpf_probe_read_str(&(data.comm), sizeof(args->child_comm), args->child_comm);
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
    bpf_probe_read_str(&(data.comm), sizeof(p->comm), p->comm);

    td_events.perf_submit(ctx, &data, sizeof(data));
    return 0;
}


// int kprobe__set_task_cpu(struct pt_regs *ctx, struct task_struct *p, unsigned int new_cpu)
// {
    // struct lb_data data = {};
    
    // data.ts = bpf_ktime_get_ns();
    // data.dst_cpu = new_cpu;
    // data.pid = p->pid;
    // data.src_cpu = p->cpu;
    // data.nr_jobs = p->se.cfs_rq->h_nr_running;
    // bpf_probe_read_str(&(data.comm), sizeof(data.comm), p->comm);

    // lb_events.perf_submit(ctx, &data, sizeof(data));
    // return 0;
// }

/*
// #define MIGRATE_FN migrate_degrades_locality
#define MIGRATE_FN can_migrate_task

int KPROBE(MIGRATE_FN) (struct pt_regs *ctx, struct task_struct *p, struct lb_env *env)
// int probe_locality(struct pt_regs *ctx, struct task_struct *p, struct lb_env *env)
{
    int cpu = bpf_get_smp_processor_id();

    struct lb_param param = {};
    param.p = p;
    param.env = env;

    lb_migrate.update(&cpu, &param);
    return 0;
}

int KRETPROBE(MIGRATE_FN) (struct pt_regs *ctx)
{
    struct lb_param *param;
    struct task_struct *p;
    struct lb_env *env;
    struct lb_data data = {};
    int cpu = bpf_get_smp_processor_id();
    int ret = PT_REGS_RC(ctx);
    
    data.ts = bpf_ktime_get_ns();

    param = (struct lb_param *)lb_migrate.lookup(&cpu);
    if (!param)
        return 0;
    p = param->p;
    env = param->env;
    
    data.pid = p->pid;
    data.src_cpu = env->src_cpu;
    data.dst_cpu = env->dst_cpu;
    data.imbalance = env->imbalance;
    data.degrades_locality = ret;

    locality_events.perf_submit(ctx, &data, sizeof(data));
    return 0;
}
*/
