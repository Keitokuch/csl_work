import json
import pandas as pd
import sys
import numpy as np


filename = sys.argv[1]

with open(filename, 'r') as f:
    latencies = pd.Series(json.load(f))

print('min', latencies.min())
print('max', latencies.max())

print(len(latencies))
print(latencies.mean())
print(latencies.std())
