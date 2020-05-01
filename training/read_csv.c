#include <stdio.h>
#include <stdlib.h>
#include <string.h>


int main()
{
    FILE* stream = fopen("predict_combined1.csv", "r");

    char line[300];
    fgets(line, 300, stream);
    while (fgets(line, 300, stream))
    {
        int i;
        char *token, *string, *tofree;
        float num;
        tofree = string = strdup(line);
        for (i = 0; i < 16; i++) {
            token = strsep(&string, ",");
            num = strtof(token, NULL);
            printf("%f ", num);
        }
        while ((token = strsep(&string, ",")) != NULL)
            printf("%s\n", token);
        // NOTE strtok clobbers tmp
        free(tofree);
    }
    return 0;
}
