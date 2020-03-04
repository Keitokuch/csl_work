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

#include "sched.h"

#ifdef CONFIG_X86_64
#define BOOT_PERCPU_OFFSET ((unsigned long)__per_cpu_load)
#else
#define BOOT_PERCPU_OFFSET 0
#endif

unsigned long __per_cpu_offset[NR_CPUS] = {
	[0 ... NR_CPUS-1] = BOOT_PERCPU_OFFSET,
};

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

#define NR_LOOPS 7
#define DUMPS_PER_LOOP 2
#define NR_PIDS  (NR_LOOPS * DUMPS_PER_LOOP)  

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
    u64 instance_ts;
    int cpu;
    int curr_pid;
    char comm[TASK_COMM_LEN];
    unsigned int h_nr_running;
    unsigned long runnable_weight;
    int pid_cnt;
    int pids[NR_PIDS];
    unsigned long weights[NR_PIDS];
};


struct lb_data {
    u64 ts;
    u64 instance_ts;
    int cpu;
    int dst_cpu;
    int src_cpu;
    int pid;
    long imbalance;
    int can_migrate;
};

struct rq_change {
    struct rq *rq;
    struct task_struct *p;
    int prev_len;
    int flags;
};

struct migrate_param {
    struct task_struct *p;
    struct lb_env *env;
    u64 instance_ts;
};

struct lb_context {
    u64 ts;
    int cpu;
};

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


BPF_HASH(lb_instance, int, struct lb_context);
BPF_HASH(lb_migrate, int, struct migrate_param);

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


int KPROBE(load_balance) (struct pt_regs *ctx, int this_cpu, struct rq *this_rq,
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
    lb_instance.update(&cpu, &lb_context);

    return 0;
}

int KPROBE(can_migrate_task) (struct pt_regs *ctx, struct task_struct *p, struct lb_env *env)
{
    struct lb_data lb_data = {};
    struct rq_data rq_data = {};
    struct rq *src_rq = env->src_rq;
    struct lb_context *lb_context;
    int cpu = bpf_get_smp_processor_id();
    u64 ts = bpf_ktime_get_ns();

    lb_data.ts = ts;
    lb_data.src_cpu = env->src_cpu;
    lb_data.dst_cpu = env->dst_cpu;

    lb_context = (struct lb_context *)lb_instance.lookup(&cpu);
    if (!lb_context)
        return 0;

    lb_data.instance_ts = lb_context->ts;
    lb_data.imbalance = env->imbalance;

    lb_env_events.perf_submit(ctx, &lb_data, sizeof(lb_data));

    rq_data.ts = ts;
    rq_data.instance_ts = lb_context->ts;
    dump_rq(&rq_data, src_rq);
    lb_src_events.perf_submit(ctx, &rq_data, sizeof(rq_data));

    struct migrate_param param = {};
    param.p = p;
    param.env = env;
    param.instance_ts = lb_context->ts;
    lb_migrate.update(&cpu, &param);

    return 0;
}

int KRETPROBE(can_migrate_task) (struct pt_regs *ctx)
{
    struct migrate_param *param;
    struct task_struct *p;
    struct lb_env *env;
    struct lb_data lb_data = {};
    int cpu = bpf_get_smp_processor_id();
    int ret = PT_REGS_RC(ctx);

    lb_data.ts = bpf_ktime_get_ns();

    param = (struct migrate_param *)lb_migrate.lookup(&cpu);
    if (!param)
        return 0;

    lb_data.instance_ts = param->instance_ts;
    p = param->p;
    env = param->env;

    lb_data.pid = p->pid;
    lb_data.dst_cpu = env->dst_cpu;
    lb_data.can_migrate = ret;

    can_migrate_events.perf_submit(ctx, &lb_data, sizeof(lb_data));
    return 0;
}
