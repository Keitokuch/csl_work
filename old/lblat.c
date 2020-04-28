#include <linux/sched.h>
#include <linux/bpf.h>

struct rq;
struct sched_domain;
enum cpu_idle_type { IGNORE };

BPF_HASH(start, int);
BPF_HISTOGRAM(dist);

int kprobe__load_balance(struct pt_regs *ctx, int cpu, struct rq *this_rq, 
        struct sched_domain *sd, enum cpu_idle_type idle,
        int *continue_balancing)
{
    u64 ts = bpf_ktime_get_ns();
    cpu = bpf_get_smp_processor_id();
    start.update(&cpu, &ts);
    return 0;
}

int kretprobe__load_balance(struct pt_regs *ctx)
{
    u64 *tsp, delta;
    int cpu = bpf_get_smp_processor_id();
    
    tsp = start.lookup(&cpu);
    if (!tsp)
        return 0;
    delta = bpf_ktime_get_ns() - *tsp;
    /* dist.increment(bpf_log2l(delta/1000)); */
    dist.increment(bpf_log2l(delta));

    start.delete(&cpu);
    return 0;
}
