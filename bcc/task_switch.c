#include <uapi/linux/ptrace.h>
#include <linux/sched.h>
#include <linux/pid_namespace.h>
#include <linux/printk.h>

/* BPF_HASH(counts, u64); */
BPF_HISTOGRAM(dist, u64);

int do_trace(struct pt_regs *ctx, struct task_struct *prev) {
    u64 pid, tgid, cpu;
    u64 *cp, count = 0;
    struct list_head *head, *pos;

    head = &(prev->tasks);

    tgid = prev->tgid;
    pid = prev->pid;
    
	/* cpu = prev->cpu; */
    cpu = bpf_get_smp_processor_id();

    /* struct task_struct *task; */
    /* pos = (head)->next; */
    /* void *__mptr = (void *)(pos); */
    /* task = ((struct task_struct *)(__mptr - offsetof(struct task_struct, se.group_node))); */
    /* cpu = task->cpu; */
    dist.increment(cpu);
    /* for (pos = (head)->next; pos != (head); pos = pos->next){ */
    /* } */
    /* list_for_each(pos, head){ */
    /*     struct task_struct *task; */
    /*     void *__mptr = (void *)(pos); */
    /*     task = ((struct task_struct *)(__mptr - offsetof(struct task_struct, se.group_node))); */
    /*     cpu = task->cpu; */
    /* } */

    /* dist.increment(cpu);  */
    /* printk(KERN_INFO "sched cpu %llu\n", cpu); */

    // cp = counts.lookup(&cpu);
    // if (pid <= 1025) {
        // cp = counts.lookup(&pid);
        // if (cp != 0) {
            // count = *cp + 1;
        // } else {
            // count = 1;
        // }

        // counts.update(&pid, &count);
    // }

    return 0;
}
