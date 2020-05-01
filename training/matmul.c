#include <stdio.h>
#include <time.h>

#define dtype float
#define m2d(x, i, j) (x)->values[i * (x)->ncol + j]
#define m1d(x, i) (x)->values[i]

struct matrix {
    int nrow;
    int ncol;
    dtype *values;
};


dtype m2[] = {
    -0.445371,  0.324039, -0.177638,  0.025281, -0.131716, -0.014088,  0.049240,  0.088052,  0.261981,  0.185080,
    0.253437,  0.158671, -0.337884, -0.015826, -0.450117, -0.234222,  0.319530, -0.209615, -0.145297, -0.248969,
    0.445135,  0.073712, -0.190644,  0.465720, -0.268109, -0.319830,  0.191638, -0.106204,  0.290370,  0.286600,
    -0.160797, -0.352717,  0.348418, -0.227029,  0.067501,  0.371882, -0.333530,  0.302885,  0.320925,  0.381000,
    0.242810,  0.042438,  0.348514, -0.429871,  0.412411, -0.232356,  0.205933,  0.000513,  0.160077, -0.332982,
    0.284923, -0.113537, -0.040797,  0.165514,  0.094682, -0.335984,  0.165898, -0.360138, -0.226556, -0.088369,
    0.097004,  0.067580, -0.467387, -0.219805, -0.186094, -0.232896, -0.312743, -0.399486,  0.067492, -0.027394,
    -0.290020, -0.267918, -0.159078, -0.043400,  0.265514, -0.280445, -0.081414, -0.016231, -0.271444, -0.264888,
    -0.308649, -0.174020,  0.291736,  0.415226, -0.309667,  0.143023, -0.441859,  0.272909, -0.008806,  0.252286,
    0.153252, -0.125371, -0.234573,  0.304578, -0.101358,  0.387908,  0.084461, -0.343828, -0.355416, -0.408393,
    -0.366552, -0.145805,  0.323116,  0.137687,  0.366815,  0.045774,  0.431171,  0.461896,  0.327402,  0.156714,
    0.281971,  0.379167, -0.007611,  0.281561, -0.137495,  0.445308,  0.222849, -0.171356, -0.012135,  0.055525,
    -0.036993,  0.409506,  0.187077,  0.448604,  0.159245,  0.201969, -0.080331, -0.255757, -0.191647,  0.367709,
    0.451462,  0.463445,  0.330726,  0.383800,  0.006644,  0.175263,  0.352838,  0.298639,  0.404415, -0.012297,
    0.460167, -0.136286,  0.308644,  0.406826, -0.454225, -0.100411, -0.082103, -0.189225,  0.193936,  0.219867,
    0.415902,  0.392218, -0.163892, -0.130250,  0.166980,  0.224535,  0.423486, -0.211085, -0.417861,  0.309534,
};

dtype m3[20];

dtype m4[] = {0,0,0,0,0,0,0,0,0,0};

dtype m5[] = { 0.704254, 0.046422, 0.072256, 0.159811, -0.452552, 0.343912, -0.697916, -0.719013, -0.200024, 0.623200 };

dtype m6[10];

dtype m7[] = {0};

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

    struct matrix W1 = {16, 10, m2};
    struct matrix out1 = {1, 10, m3};
    struct matrix B1 = {1, 10, m4};

    struct matrix W2 = {10, 1, m5};
    struct matrix out2 = {1, 1, m6};
    struct matrix B2 = {1, 1, m7};

    clock_t t;

    /* t = clock(); */
    matmul(input, &W1, &out1);
    /* t = clock() - t; */
    /* float time_taken = ((float)t)/CLOCKS_PER_SEC; */
    /* printf("matmul time: %f\n", time_taken); */

    ReLU(&out1);

    matadd(&out1, &B1, &out1);

    matmul(&out1, &W2, &out2);

    output = m1d(&out2, 0);

    /* printf("output: %f\n", output); */
    
    return output > 0.5 ? 1 : 0;
}

int main()
{
    int prediction;
    dtype m1[] = {
        0,1,0,0,1,1,1,1,0,0.16399999999999998,0.001,0,0,0.0,0,0
    };
    struct matrix input = {1, 16, m1};
    clock_t t;

    t = clock();
    prediction = forward_pass(&input);
    t = clock() - t;
    float time_taken = ((float)t)/CLOCKS_PER_SEC;

    printf("prediction: %d\n", prediction);
    printf("execution time: %f\n", time_taken);

    return 0;
}
