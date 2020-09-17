import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def autolabel(rects, side, color):
    """
    Attach a text label above each bar displaying its height
    """
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2. + side, 1.05*height,
                f'{height:.2f}',
                ha='center', va='bottom', fontsize=font['size']-3, color=color)


import matplotlib
from plot_config import font
matplotlib.rc('font', **font)
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42


mlps = (24.8142, 38.7243, 32.1692, 26.7509, 18.9275, 4.7194, 7.4541)
linuxs = (24.5136, 40.7327, 31.8502, 27.0456, 18.4986, 4.65535, 7.46905)

mlp_std = (0.677403395, 0.665265969, 0.229969476, 0.583376971, 0.259326146, 0.125950149, 0.128887121)
linux_std = (0.228695081, 1.701304855, 0.173082524, 0.696502721, 0.140709772, 0.122505622, 0.191649022)

indices = range(len(mlps))
categs = [' ', 'blackscholes', 'dedup', 'ferret', 'freqmine', 'swaptions', 'fibo 20', 'fibo 21']

width = np.min(np.diff(indices))/3.

fig = plt.figure()
alpha = 0.75

ax = fig.add_subplot(111)
rects1 = ax.bar(indices-width/2., linuxs, width, yerr=linux_std,
                color='tab:blue', alpha=alpha, label='-Ymin')
rects2 = ax.bar(indices+width/2., mlps, width, yerr=mlp_std,
                color='tab:orange', alpha=alpha, label='Ymax')
#tiks = ax.get_xticks().tolist()
ax.axes.set_xticklabels(categs)
#  ax.set_xlabel('benchmark programs')
ax.set_ylabel('Runtime (s)')
ax.set_ylim(top=50)
#  ax.set_title('Mean Runtime of Benchmark Programs')

autolabel(rects1, side=-0.1, color='blue')
autolabel(rects2, side=0.1, color='red')
ax.legend((rects1[0], rects2[0]), ('Linux', 'ML'))
plt.show()
