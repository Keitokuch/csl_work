import sys
import pickle
import numpy

tag = sys.argv[1]
weight_file = 'pickle_' + tag + '.weights'

fm = 0

with open(weight_file, 'rb') as f:
    weights = pickle.load(f)

if fm == 0:
    for weight_entry in weights:
        for line in weight_entry:
            try:
                print(', '.join([f'{f: 8f}' for f in line]))
            except:
                print(line)
        print()
elif fm == 1:
    for weight_entry in weights:
        ret = []
        for line in weight_entry:
            try:
                for f in line:
                    ret.append(f)
            except:
                ret.append(line)

        print(', '.join([f'{f: 8f}' for f in ret]))
