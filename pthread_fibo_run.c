#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>

void *runner(void *x);
int fibo(int x);

int main(int argc, char *argv[]) {
    pthread_attr_t attr;
    int count, i;
    void *ret;

    if (argc != 2) {
		fprintf(stderr,"usage: pthreads <integer value>\n");
		return -1;
	}

	count = atoi(argv[1]);

	if (count < 1) {
		fprintf(stderr,"%d must be>= 1\n", count);
		return -1;
	}

    pthread_t *threads = (pthread_t *)malloc(count * sizeof(pthread_t));

    pthread_attr_init(&attr);

    for (i = 0; i < count; i++) {
        pthread_create(&threads[i], &attr, runner, (void *)i);
    }

    for (i = 0; i < count; i++) {
        pthread_join(threads[i], NULL);
    }

    return 0;
}


void *runner(void *x) {
    int n = fibo((int)x);
    
    printf("%dth fibo: %d\n", (int)x, n);
}

int fibo(int x) {
    if (x <= 1) {
        return 1;
    }
    return fibo(x - 1) + fibo(x - 2);
}
