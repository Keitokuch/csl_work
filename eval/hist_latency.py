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
parser.add_argument('-t', '--thread', action='store')
parser.add_argument('-s', '--split', action='store_true')

args = parser.parse_args()
#  SAMPLE_SIZE = 1200000 if args.thread == '80' else 100000
FUNC_NAME = 'can_migrate_task' if args.func == 'cm' else 'load_balance'
args.thread = args.thread or '80'
right = 6000 if args.func == 'cm' else 100000
top = 0.0015 if args.func == 'cm' else 0.00011
nr_bin = 100
bins = range(0, right, right // nr_bin)

colors = ['tab:blue', 'tab:orange', 'tab:pink']
labels = ['Linux', 'MLP Floating Point', 'MLP Fixed Point']
titles = ['Linux', 'MLP in Floating Point', 'MLP in Fixed Point']
tags = ['linux', 'mlp', 'fxdpt']


#  func = sys.argv[1]
#  model = sys.argv[2]
#  th = sys.argv[3]
def plot_hist(plt, data, bins, label, color=None, alpha=0.75):
    global right, top
    avg = data.mean()
    std = data.std()
    label = f'{label}\nmean={avg:.0f},std={std:.0f}'
    n, bins, patches = plt.hist(data, bins=bins, density=True, color=color, alpha=alpha, label=label)
    #  color='tab:red'
    plt.axvline(avg, color=color, linestyle='-', linewidth=1, alpha=alpha+0.2)
    plt.axvline(avg+std, color=color, linestyle='--', linewidth=1, alpha=alpha)
    plt.axvline(avg-std, color=color, linestyle='--', linewidth=1, alpha=alpha)
    plt.set_xlim(right=right)
    plt.set_ylim(top=top)
    plt.legend(fontsize='small')
    plt.grid(axis='y', alpha=0.4)
    return n, bins, patches

if args.model:
    filename = f'latency_{args.func}_{args.model}80.json'
    if args.model == 'linux' :
        model_name = 'Linux'
        color = 'tab:blue'
        tag = 'Linux'
    elif args.model == 'mlp':
        model_name = 'MLP in Floating Point'
        color = 'tab:orange'
        tag = 'MLP Floating Point'
    else:
        model_name = 'MLP in Fixed Point'
        color = 'tab:pink'
        tag = 'MLP Fixed Point'

    latencies = read_series(filename)

    plt.grid(axis='y', alpha=0.75)
    plot_hist(plt, latencies, bins=bins, color=color, label=tag)
    plt.xlim(right=right)
    plt.ylim(top=top)
    plt.grid(axis='y', alpha=0.4)
    plt.legend(fontsize='small')
    plt.title('Latency of function {} with {}'.format(FUNC_NAME, model_name))
    plt.xlabel('Latency (ns)')
    plt.ylabel('Density')
    plt.show()
elif args.split:
    plt.figure(1)
    fig, axes = plt.subplots(1, 3, figsize=(16, 5), sharey='row')
    data = []
    for model in tags:
        filename = f'latency_cm_{model}{args.thread}.json'
        latencies = read_series(filename) #.sample(SAMPLE_SIZE)
        print(model, len(latencies))
        data.append(latencies)
    for i in range(3):
        plot_hist(axes[i], data[i], bins=bins, color=colors[i], label=labels[i])
    fig.suptitle('Latency of function {}'.format(FUNC_NAME))
    axes[1].set_xlabel('Latency (ns)')
    axes[0].set_ylabel('Density')

    plt.figure(1)
    fig, axes = plt.subplots(1, 3, figsize=(16, 5), sharey='row')
    data = []
    for model in tags:
        filename = f'latency_lb_{model}{args.thread}.json'
        latencies = read_series(filename) #.sample(SAMPLE_SIZE)
        print(model, len(latencies))
        data.append(latencies)
    for i in range(3):
        plot_hist(axes[i+3], data[i+3], bins=bins, color=colors[i], label=labels[i])
    fig.suptitle('Latency of function {}'.format(FUNC_NAME))
    axes[1].set_xlabel('Latency (ns)')
    axes[0].set_ylabel('Density')

    for i in range(3):
        axes[i].set_title(titles[i])
        axcdf = axes[i].twinx()
        axcdf.hist(data[i], bins=1000, density=True, cumulative=True,
                   histtype='step', alpha=0.8, color='blue')
    plt.show()

else:
    data = []
    for model in ['linux', 'MLP', 'fxdpt']:
        filename = f'latency_{args.func}_{model}{args.thread}.json'
        latencies = read_series(filename) #.sample(SAMPLE_SIZE)
        print(model, len(latencies))
        data.append(latencies)
    #  right = max(map(max, data))
    bins = range(0, right, right // nr_bin)
    plot_hist(plt, data[0], bins=bins, color='tab:blue', label='Linux')
    plot_hist(plt, data[1], bins=bins, color='tab:orange', label='MLP Floating Point')
    plot_hist(plt, data[2], bins=bins, color='yellow', label='MLP Fixed Point')
    #  plt.hist(data, bins=bins, label=['Linux', 'MLP', 'FixedPt'], density=True)
    #  plt.xlim(right=max(data[0].max(), data[1].max()))
    plt.legend(fontsize='small')
    plt.xlabel('Latency (ns)')
    plt.ylabel('Density')
    #  plt.title('Latency of function {} with {}'.format(FUNC_NAME, 'Linux'))
    #  plt.title('Latency of function {} with {}'.format(FUNC_NAME, 'MLP in Floating Point'))
    plt.title('Latency of function {} with {}'.format(FUNC_NAME, 'MLP in Fixed Point'))

    plt.show()
