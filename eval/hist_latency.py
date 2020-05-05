import json
import matplotlib.pyplot as plt
import pandas as pd
import sys
import numpy as np
from scipy.stats import zscore

SAMPLE_SIZE = 100000

func = sys.argv[1]
model = sys.argv[2]

filename = f'latency_{func}_{model}.json'

with open(filename, 'r') as f:
    latencies = pd.Series(json.load(f))

z_scores = zscore(latencies)
filtered_entries = np.abs(z_scores) < 2
latencies = latencies[filtered_entries].sample(SAMPLE_SIZE)

n, bins, patches = plt.hist(x=latencies, bins='auto', color='#0504aa',
                            alpha=0.7, rwidth=1)
plt.grid(axis='y', alpha=0.75)
plt.xlabel('Value')
plt.ylabel('Frequency')
plt.title('My Very Own Histogram')
plt.text(1000, 1000, f'mean={latencies.mean():.0f}, std={latencies.std():.0f}')
plt.show()
