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
    filtered = np.abs(z_scores) < 3
    return series[filtered]


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
    data = []
    _ = plt.figure(figsize=(3.5, 1.5))
    #  for model in ['linux', 'mlp', 'fxdpt']:
    for model in ['linux', 'mlp']:
        filename = f'imbalance_{model}.json'
        imba = read_series(filename).sample(SAMPLE_SIZE)
        print(model, len(imba))
        data.append(imba)
    #  bins = SAMPLE_SIZE // 5000
    #  plot_hist2(data, label=['Linux', 'ML', 'Fxdpt'])
    plot_hist2(data, label=['Linux', 'ML'])
    #  bins = 'auto'
    #  _, _, _ = plot_hist(data[0], bins=bins, color='tab:blue', label='Linux')
    #  plot_hist(data[1], bins=bins, color='tab:orange', label='ML')
    plt.xlim(right=max(data[0].max(), data[1].max()))
    plt.grid(axis='y', alpha=0.4)
    plt.legend(fontsize=11)
    plt.xlabel('Max Imbalance (jobs)')
    plt.ylabel('PDF')
    #  plt.title('Histogram of Max Imbalance of models')

    plt.show()
