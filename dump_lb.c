#include <uapi/linux/ptrace.h>
#include <linux/sched.h>
#include <bcc/proto.h>
#include <linux/bpf.h>
#include <linux/kernel.h>
#include <linux/sched/topology.h>
#include <linux/percpu.h>
#include <linux/sched/mm.h>
#include <linux/percpu.h>
#include <linux/migrate.h>
#include <linux/mm.h>
#include <linux/smp.h>
#include <linux/percpu-defs.h>
#include <uapi/linux/bpf.h>

#include "dump_lb.h"

/* ====== NUMA related ====== */
/* Shared or private faults. */
#define NR_NUMA_HINT_FAULT_TYPES 2

/* Memory and CPU locality */
#define NR_NUMA_HINT_FAULT_STATS (NR_NUMA_HINT_FAULT_TYPES * 2)

/* Averaged statistics, and temporary buffers. */
#define NR_NUMA_HINT_FAULT_BUCKETS (NR_NUMA_HINT_FAULT_STATS * 2)


#undef offsetof
#define offsetof(TYPE, MEMBER) ((size_t) &((TYPE *)0)->MEMBER)
#undef container_of
#define container_of(ptr, type, member) ({				\
    ((type *)((void *)(ptr) - offsetof(type, member))); })


#define KPROBE(fn)  _KPROBE(fn)
#define _KPROBE(fn) kprobe__##fn
#define KRETPROBE(fn)  _KRETPROBE(fn)
#define _KRETPROBE(fn) kretprobe__##fn


static inline int task_faults_idx(enum numa_faults_stats s, int nid, int priv)
{
	return NR_NUMA_HINT_FAULT_TYPES * (s * nr_node_ids + nid) + priv;
}

static inline unsigned long task_faults(struct task_struct *p, int nid)
{
	if (!p->numa_faults)
		return 0;

	return p->numa_faults[task_faults_idx(NUMA_MEM, nid, 0)] +
		p->numa_faults[task_faults_idx(NUMA_MEM, nid, 1)];
}


BPF_HASH(lb_instances, int, struct lb_context);

BPF_PERF_OUTPUT(dq_events);
BPF_PERF_OUTPUT(eq_events);
BPF_PERF_OUTPUT(rq_events);
BPF_PERF_OUTPUT(tn_events);
BPF_PERF_OUTPUT(td_events);
/* BPF_PERF_OUTPUT(tsk_events); */
BPF_PERF_OUTPUT(rn_events);
BPF_PERF_OUTPUT(lb_dst_events);
BPF_PERF_OUTPUT(lb_src_events);
BPF_PERF_OUTPUT(lb_env_events);
BPF_PERF_OUTPUT(can_migrate_events);
/* BPF_PERF_OUTPUT(locality_events); */


static void dump_rq(struct rq_data *data, struct rq *rq) {

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
    data->h_nr_running = cfs->h_nr_running;
    data->runnable_weight = cfs->runnable_weight;
    data->pid_cnt = 0;

    head = &(rq->cfs_tasks);
    pos = head;
    int j = 0;
    for (i = 0; i < NR_LOOPS; i++) {
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

#define EQ_FN enqueue_task_fair
#define DQ_FN dequeue_task_fair

int (load_balance) (struct pt_regs *ctx, int this_cpu, struct rq *this_rq,
			struct sched_domain *sd, enum cpu_idle_type idle,
			int *continue_balancing)
{
    struct rq_data rq_data = {};
    struct lb_context lb_context = {};
    u64 ts = bpf_ktime_get_ns();
    int cpu = bpf_get_smp_processor_id();
    rq_data.ts = ts;
    rq_data.instance_ts = ts;
    lb_context.ts = ts;
    lb_context.cpu = cpu;

    dump_rq(&rq_data, this_rq);
    lb_dst_events.perf_submit(ctx, &rq_data, sizeof(rq_data));
    lb_instances.update(&cpu, &lb_context);

    return 0;
}

int KPROBE(can_migrate_task) (struct pt_regs *ctx, struct task_struct *p, struct lb_env *env)
{
    struct lb_data lb_data = {};
    struct rq *src_rq = env->src_rq;
    struct rq *dst_rq = env->dst_rq;
    struct lb_context lb_context = {};
    int cpu = bpf_get_smp_processor_id();
    u64 ts = bpf_ktime_get_ns();

    lb_context.ts = ts;
    lb_context.cpu = cpu;
    lb_context.p = p;
    lb_context.env = env;
    lb_instances.update(&cpu, &lb_context);

    lb_data.ts = ts;
    lb_data.instance_ts = ts;

    lb_data.src_cpu = env->src_cpu;
    lb_data.dst_cpu = env->dst_cpu;
    lb_data.imbalance = env->imbalance;
    lb_data.env_idle = env->idle;

    lb_data.pid = p->pid;
    lb_data.numa_preferred_nid = p->numa_preferred_nid;
    lb_data.p_policy = p->policy;
    lb_data.p_running = p->on_cpu;

    lb_data.src_nr_running = src_rq->nr_running;
    lb_data.src_nr_numa_running = src_rq->nr_numa_running;
    lb_data.src_nr_preferred_running = src_rq->nr_preferred_running;

    lb_data.delta = src_rq->clock_task - p->se.exec_start;

    lb_env_events.perf_submit(ctx, &lb_data, sizeof(lb_data));

    return 0;
}

int KRETPROBE(can_migrate_task) (struct pt_regs *ctx)
{
    struct task_struct *p;
    struct lb_env *env;
    struct lb_ret_data lb_ret_data = {};
    struct lb_context *context;
    int cpu = bpf_get_smp_processor_id();
    int ret = PT_REGS_RC(ctx);

    lb_ret_data.ts = bpf_ktime_get_ns();

    context = (struct lb_context *)lb_instances.lookup(&cpu);
    if (!context)
        return 0;

    lb_ret_data.instance_ts = context->ts;
    p = context->p;
    env = context->env;

    lb_ret_data.pid = p->pid;
    lb_ret_data.dst_cpu = env->dst_cpu;
    lb_ret_data.can_migrate = ret;

    can_migrate_events.perf_submit(ctx, &lb_ret_data, sizeof(lb_ret_data));
    return 0;
}
