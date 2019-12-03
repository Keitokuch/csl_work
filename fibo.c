#include <stdio.h>

int main() {
    long long i, prev, curr, temp;
    for (i = 0, prev = 0, curr = 1; i < 1000000; i++) {
       temp = prev + curr;
       prev = curr;
       curr = temp;
       printf("%lld ", curr);
    }
    return 0;
}

