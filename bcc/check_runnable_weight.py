from __future__ import print_function
from bcc import BPF, PerfType, PerfSWConfig
from time import sleep, strftime
from tempfile import NamedTemporaryFile
from os import open, close, dup, unlink, O_WRONLY
# Linux 4.15 introduced a new field runnable_weight
# in linux_src:kernel/sched/sched.h as
#     struct cfs_rq {
#         struct load_weight load;
#         unsigned long runnable_weight;
#         unsigned int nr_running, h_nr_running;
#         ......
#     }
# and this tool requires to access nr_running to get
# runqueue len information.
#
# The commit which introduces cfs_rq->runnable_weight
# field also introduces the field sched_entity->runnable_weight
# where sched_entity is defined in linux_src:include/linux/sched.h.
#
# To cope with pre-4.15 and 4.15/post-4.15 releases,
# we run a simple BPF program to detect whether
# field sched_entity->runnable_weight exists. The existence of
# this field should infer the existence of cfs_rq->runnable_weight.
#
# This will need maintenance as the relationship between these
# two fields may change in the future.
#
def check_runnable_weight_field():
    # Define the bpf program for checking purpose
    bpf_check_text = """
#include <linux/sched.h>
unsigned long dummy(struct sched_entity *entity)
{
    return entity->runnable_weight;
}
"""

    # Get a temporary file name
    tmp_file = NamedTemporaryFile(delete=False)
    tmp_file.close();

    # Duplicate and close stderr (fd = 2)
    old_stderr = dup(2)
    close(2)

    # Open a new file, should get fd number 2
    # This will avoid printing llvm errors on the screen
    fd = open(tmp_file.name, O_WRONLY)
    try:
        t = BPF(text=bpf_check_text)
        success_compile = True
    except:
        success_compile = False

    # Release the fd 2, and next dup should restore old stderr
    close(fd)
    dup(old_stderr)
    close(old_stderr)

    # remove the temporary file and return
    unlink(tmp_file.name)
    print(success_compile)
    return success_compile

check_runnable_weight_field()
