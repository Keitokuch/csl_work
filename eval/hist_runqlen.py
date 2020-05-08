import json
import matplotlib.pyplot as plt
import pandas as pd
import sys
import numpy as np
from scipy.stats import zscore
import argparse

def read_dict(filename):
    with open(filename, 'r') as f:
        raw_dict = json.load(f)
    total = sum(raw_dict.values())
    hist_runqlen = {int(k): v/total for k, v in raw_dict.items() if v >= 10}
    #  hist_runqlen = {int(k): v for k, v in raw_dict.items() if v >= 10}
    return hist_runqlen


parser = argparse.ArgumentParser()
parser.add_argument('-m', '--model', action='store')
parser.add_argument('-s', '--size', action='store')

args = parser.parse_args()

SAMPLE_SIZE = args.size or 6500

#  func = sys.argv[1]
#  model = sys.argv[2]
#  th = sys.argv[3]
def plot_hist(data, bins, color, label, alpha=0.7):
    avg = data.mean()
    std = data.std()
    label = f'{label}\nmean={avg:.2f},std={std:.2f}'
    n, bins, patches = plt.hist(data, bins=bins, color=color, alpha=alpha, label=label)
    plt.axvline(avg, color=color, linestyle='-', linewidth=1, alpha=alpha+0.2)
    plt.axvline(avg+std, color=color, linestyle='--', linewidth=1, alpha=alpha)
    plt.axvline(avg-std, color=color, linestyle='--', linewidth=1, alpha=alpha)
    return n, bins, patches

def plot_hist2(data, label, alpha=0.85):
    bins = range(np.max(data))
    n, bins, _ = plt.hist(data, bins=bins, density=True, alpha=alpha, label=label)
    print(n, bins)

if args.model:
    filename = f'imbalance_{args.model}.json'

    #  imba = read_series(filename).sample(SAMPLE_SIZE)
    imba = read_series(filename)

    n, bins, patches = plt.hist(imba, bins='auto', alpha=0.7, rwidth=1)
    print(n)
    plt.xticks(np.arange(min(imba), max(imba)+1, 2.0))
    plt.grid(axis='y', alpha=0.6)
    plt.xlabel('Max Imbalance (jobs)')
    plt.ylabel('Frequency')
    plt.title('Histogram of Max Imbalance')
    plt.show()
else:
    hists = []
    for model in ['linux', 'mlp']:
        filename = f'runqlen_{model}.json'
        hist_runqlen = read_dict(filename)
        hists.append(hist_runqlen)
    bins = hists[0].keys()
    width = 0.4
    #  bins = SAMPLE_SIZE // 5000
    #  bins = 'auto'
    plt.bar(bins, hists[0].values(), width, color='tab:blue', alpha=0.85, label='Linux')
    plt.bar([k + width for k in hists[1].keys()], hists[1].values(), width,
            color='tab:orange', alpha=0.6, label='ML')

    #  plt.hist(*hists[1].items(), bins=bins, color='tab:orange', label='ML')
    #  plt.xlim(right=max(data[0].max(), data[1].max()))
    plt.grid(axis='y', alpha=0.4)
    plt.yscale('log')
    plt.legend(fontsize='small')
    plt.xlabel('Number of Running Jobs')
    plt.ylabel('Density')
    plt.title('Distribution of Runqueue Length')

    plt.show()
