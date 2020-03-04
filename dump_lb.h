#include "sched.h"

#define NR_LOOPS 7
#define DUMPS_PER_LOOP 2
#define NR_PIDS  (NR_LOOPS * DUMPS_PER_LOOP)  

#define NR_NODES 2

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

struct migrate_data {
    u64 ts;
    u64 instance_ts;
    int cpu;
    int dst_cpu;
    int src_cpu;
    int pid;
    long imbalance;
    int numa_preferred_nid;
    unsigned int src_nr_running;
    unsigned int src_nr_numa_running;
    unsigned int src_nr_preferred_running;
    int env_idle;
    s64 delta;
    unsigned int p_policy;
    int p_running;
    unsigned long p_numa_faults[NR_NODES];
    int can_migrate;
};

struct lb_ret_data {
    u64 ts;
    u64 instance_ts;
    int pid;
    int dst_cpu;
    int can_migrate;
};

struct lb_context {
    u64 ts;
    int cpu;
    struct task_struct *p;
    struct lb_env *env;
};

struct can_migrate_context {
    u64 ts;
    int cpu;
    struct task_struct *p;
    struct lb_env *env;
    struct migrate_data data;
};
