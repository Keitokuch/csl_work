#include <stdio.h>
#include <time.h>

#include "c_mlp.h"

#define NR_FEAT     15

#define dtype float
#define m2d(x, i, j) ((x)->values[i * (x)->ncol + j])
#define m1d(x, i) ((x)->values[i])
#define ftox(f)     (*(unsigned *)&((float){f}))

struct matrix {
    int nrow;
    int ncol;
    dtype *values;
};

void print_matrix(struct matrix *X)
{
    int i, j;

    for(i=0; i<X->nrow; i++)
    {
        printf("\n\t");
        for(j=0; j<X->ncol;j++)
        {
            printf("%f\t", m2d(X, i, j));
        }
    }
    printf("\n");
}

int matmul(struct matrix *X, struct matrix *Y, struct matrix *Z) 
{
    int i, j, k;
    for(i = 0; i < X->nrow; i++)
        for(j = 0; j < Y->ncol; j++)
            for(k = 0; k < X->ncol; k++)
            {
                m2d(Z, i, j) = m2d(Z, i, j) + (m2d(X, i, k) * m2d(Y, k, j));
                /* z[i][j] = z[i][j] + (x[i][k] * y[k][j]); */
            }
    return 0;
}

int matadd(struct matrix *X, struct matrix *Y, struct matrix *Z)
{
    int i;
    /* if (X->nrow * X->ncol != Y->nrow * Y->ncol) { */
    /*     printf("Mat add size unmatching\n"); */
    /*     return 1; */
    /* } */
    for (i = 0; i < X->nrow * X->ncol; i++) {
        Z->values[i] = X->values[i] + Y->values[i];
    }
}

dtype _ReLU(dtype x) { return x > 0 ?  x : 0;}

void ReLU(struct matrix *X)
{
    int i;
    for (i = 0; i < X->nrow * X->ncol; i++) {
        X->values[i] = _ReLU(X->values[i]);
    }
}

int forward_pass(struct matrix *input){
    float output;
    dtype o1[10] = {0};
    dtype o2[10] = {0};

    struct matrix W1 = {NR_FEAT, 10, w1};
    struct matrix out1 = {1, 10, o1};
    struct matrix B1 = {1, 10, b1};
    struct matrix W2 = {10, 1, w2};
    struct matrix out2 = {1, 1, o2};
    struct matrix B2 = {1, 1, b2};
    printf("print_hex test: %08x\n", ftox(-2.322));

    /* clock_t t; */
    /* t = clock(); */
    matmul(input, &W1, &out1);
    /* t = clock() - t; */
    /* float time_taken = ((float)t)/CLOCKS_PER_SEC; */
    /* printf("matmul time: %f\n", time_taken); */

    matadd(&out1, &B1, &out1);

    ReLU(&out1);

    matmul(&out1, &W2, &out2);

    matadd(&out2, &B2, &out2);

    output = m1d(&out2, 0);

    printf("output: %x\n", output);
    
    return output > 0.5 ? 1 : 0;
}

int main()
{
    int prediction;
    dtype mval[] = {
        1,0,1,0,0,1,0,0,0,0.096,0.0,0,0.0,0,0
    };
    struct matrix input = {1, NR_FEAT, mval};
    clock_t t;

    t = clock();
    prediction = forward_pass(&input);
    t = clock() - t;
    float time_taken = ((float)t)/CLOCKS_PER_SEC;

    printf("prediction: %d\n", prediction);
    printf("execution time: %f\n", time_taken);

    return 0;
}
