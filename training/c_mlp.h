#ifndef C_MLP_H
#define C_MLP_H

#include <stdio.h>
#include <stdlib.h>

#define dtype float

/*
dtype w1[] = {
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


dtype b1[] = {0,0,0,0,0,0,0,0,0,0};

dtype w2[] = { 0.704254, 0.046422, 0.072256, 0.159811, -0.452552, 0.343912, -0.697916, -0.719013, -0.200024, 0.623200 };

dtype b2[] = {0};
*/

dtype w1[] = {
    0.063470, -0.428658, -0.015314,  0.277778, -0.198408,  0.028286, -0.143228,  0.079590,  0.253528,  0.302190,
    1.447406, -0.572227,  0.341534, -0.362629, -0.501773,  0.690353, -0.002165, -0.233555,  0.266883, -0.123887,
    -0.416813,  0.384499, -0.137676,  0.458163, -0.101651, -0.877348, -0.428748,  0.207880,  0.051600, -0.419831,
    0.242046,  0.047132, -0.676614, -0.413490, -0.179147,  0.106640,  0.279093,  1.057631,  0.657507, -0.076880,
    -0.607351,  0.356799,  0.325137,  0.080807, -0.094649,  0.178554,  0.125266,  0.425049,  0.303428,  0.235473,
    0.217006,  0.186698, -0.210308,  0.249756, -0.201977, -0.190288, -0.371634,  0.031270, -0.148155,  0.148701,
    0.113428, -0.157046,  0.621261,  0.033086,  0.472668,  0.164127, -0.489429, -0.151315,  0.006256, -0.271532,
    -0.581515, -0.068720,  0.231347,  0.131845,  0.192878, -0.106196, -0.418927,  0.092760, -0.149129,  0.158241,
    0.074568, -0.047864, -0.005001,  0.123267, -0.799139,  0.273663, -0.291142,  0.038058,  0.304975,  0.260158,
    -0.669749, -1.926163,  0.771760, -0.096699,  0.617437,  0.722506, -0.063218, -0.705696, -0.847272, -0.124060,
    1.102030, -2.326984, -2.911482, -0.737141, -0.284186, -0.012587,  0.236148,  0.539290,  0.618522,  0.582792,
    0.214454, -0.301156,  0.027861,  0.301879, -0.106406, -0.082700, -0.175790, -0.015568,  0.262186,  0.425974,
    0.008119,  0.222719,  0.476276,  0.227657,  0.148310, -0.311300, -0.254819, -0.439265, -0.429555, -0.282567,
    -0.211727, -0.218961, -1.334227, -1.381104,  0.606033, -1.579762,  0.095911,  2.104315,  1.861555,  1.315512,
    -1.081356,  1.028658, -0.119388, -0.269990, -0.124105,  0.105574,  0.095064,  0.827121,  0.242849,  0.645179,
    0.477025, -0.044399,  0.738871,  0.796732, -0.002416,  0.403498, -0.164278, -0.481705, -0.919492, -0.761857
};

dtype b1[] = {
    -0.3316112, -0.039475158, -0.05952318, -0.12049943, 0.13199526, 0.07495853, -0.11268558, 0.2277887, -0.0010862548, 0.013734841
};

dtype w2[] = {-0.966899, -1.118419, -0.352490, -0.074255,  0.878286, -0.328997,  0.276641,  0.921186,  0.464391,  0.093770};

dtype b2[] = {0.04416889};

#endif
