#include <unistd.h>
#include <sys/syscall.h>
#include <stdio.h>

int main(int argc, const char *argv[]) {
    int ret;
    if (argc != 2) {
        printf("invalid operand\n");
        return 1;
    }
    if (argv[1][0] == '0') {
        ret = syscall(335, 0);
        printf("sched log off\n");
    } else if (argv[1][0] == '1') {
        ret = syscall(335, 1);
        printf("sched log on\n");
    }
    return 0;
}
