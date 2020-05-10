import json
import matplotlib.pyplot as plt
import pandas as pd
import sys
import numpy as np
from scipy.stats import zscore
import argparse

def read_series(filename):
    with open(filename, 'r') as f:
        series = pd.Series(json.load(f))
    z_scores = zscore(series)
    filtered = np.abs(z_scores) < 2
    return series[filtered]


parser = argparse.ArgumentParser()
parser.add_argument('func', action='store')
parser.add_argument('-m', '--model', action='store')
parser.add_argument('-t', '--thread', action='store', required=True)

args = parser.parse_args()
SAMPLE_SIZE = 1200000 if args.thread == '80' else 100000
FUNC_NAME = 'can_migrate_task' if args.func == 'cm' else 'load_balance'


#  func = sys.argv[1]
#  model = sys.argv[2]
#  th = sys.argv[3]
def plot_hist(data, bins, label, color=None, alpha=0.75):
    avg = data.mean()
    std = data.std()
    label = f'{label}\nmean={avg:.0f},std={std:.0f}'
    n, bins, patches = plt.hist(data, bins=bins, density=True, color=color, alpha=alpha, label=label)
    plt.axvline(avg, color=color, linestyle='-', linewidth=1, alpha=alpha+0.2)
    plt.axvline(avg+std, color=color, linestyle='--', linewidth=1, alpha=alpha)
    plt.axvline(avg-std, color=color, linestyle='--', linewidth=1, alpha=alpha)
    return n, bins, patches

if args.model:
    filename = f'latency_{args.func}_{args.model}{args.thread}.json'

    #  latencies = read_series(filename).sample(SAMPLE_SIZE)
    latencies = read_series(filename)

    n, bins, patches = plt.hist(x=latencies, bins='auto', color='#0504aa',
                                alpha=0.7, rwidth=1)
    plt.grid(axis='y', alpha=0.75)
    plt.xlabel('Latency (ns)')
    plt.ylabel('Frequency')
    plt.title('My Very Own Histogram')
    plt.text(1000, 1000, f'mean={latencies.mean():.0f}, std={latencies.std():.0f}')
    plt.show()
else:
    data = []
    for model in ['linux', 'MLP', 'fxdpt']:
        filename = f'latency_{args.func}_{model}{args.thread}.json'
        latencies = read_series(filename) #.sample(SAMPLE_SIZE)
        print(model, len(latencies))
        data.append(latencies)
    bins = 100
    nr_bin = 50
    right = max(map(max, data))
    bins = range(0, right, right // nr_bin)
    n, newbins, _ = plot_hist(data[0], bins=bins, color='tab:blue', label='Linux')
    plot_hist(data[1], bins=newbins, color='tab:orange', label='ML')
    plot_hist(data[2], bins=newbins, color='tab:pink', label='FixedPt')
    #  plt.hist(data, bins=bins, label=['Linux', 'MLP', 'FixedPt'], density=True)
    plt.xlim(right=max(data[0].max(), data[1].max()))
    plt.grid(axis='y', alpha=0.4)
    plt.legend(fontsize='small')
    plt.xlabel('Latency (ns)')
    plt.ylabel('Frequency')
    plt.title('Latency of function {}'.format(FUNC_NAME))

    plt.show()
