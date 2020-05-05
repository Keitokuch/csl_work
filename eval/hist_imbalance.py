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
    filtered = np.abs(z_scores) < 5
    return series[filtered]


parser = argparse.ArgumentParser()
parser.add_argument('-m', '--model', action='store')
parser.add_argument('-s', '--size', action='store')

args = parser.parse_args()

#  SAMPLE_SIZE = args.size or 2500

#  func = sys.argv[1]
#  model = sys.argv[2]
#  th = sys.argv[3]
def plot_hist(data, bins, color, label, alpha=0.65):
    avg = data.mean()
    std = data.std()
    label = f'{label}\nmean={avg:.0f},std={std:.0f}'
    n, bins, patches = plt.hist(data, bins=bins, color=color, alpha=alpha, label=label)
    plt.axvline(avg, color=color, linestyle='-', linewidth=1, alpha=alpha+0.2)
    plt.axvline(avg+std, color=color, linestyle='--', linewidth=1, alpha=alpha)
    plt.axvline(avg-std, color=color, linestyle='--', linewidth=1, alpha=alpha)
    return n, bins, patches

if args.model:
    filename = f'imbalance_{args.model}.json'

    #  imba = read_series(filename).sample(SAMPLE_SIZE)
    imba = read_series(filename)

    n, bins, patches = plt.hist(imba, bins='auto', alpha=0.7, rwidth=1)
    print(n)
    plt.xticks(np.arange(min(imba), max(imba)+1, 1.0))
    plt.grid(axis='y', alpha=0.6)
    plt.xlabel('Max Imbalance (jobs)')
    plt.ylabel('Frequency')
    plt.title('Histogram of Max Imbalance')
    plt.show()
else:
    data = []
    for model in ['mlp', 'linux']:
        filename = f'imbalance_{model}.json'
        imba = read_series(filename).sample(SAMPLE_SIZE)
        print(model, len(imba))
        data.append(imba)
    #  bins = SAMPLE_SIZE // 5000
    n, bins, _ = plot_hist(data[1], bins='auto', color='tab:blue', label='Linux')
    plot_hist(data[0], bins=bins, color='tab:orange', label='ML')
    plt.xlim(right=max(data[0].max(), data[1].max()))
    plt.grid(axis='y', alpha=0.4)
    plt.legend(fontsize='small')
    plt.xlabel('Max Imbalance (ns)')
    plt.ylabel('Frequency')
    plt.title('Histogram of Max Imbalance of models')

    plt.show()
