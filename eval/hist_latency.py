import json
import matplotlib.pyplot as plt

filename='output'

with open(filename, 'r') as f:
    latencies = json.load(f)

n, bins, patches = plt.hist(x=latencies, bins='auto', color='#0504aa',
                            alpha=0.7, rwidth=0.85)
plt.grid(axis='y', alpha=0.75)
plt.xlabel('Value')
plt.ylabel('Frequency')
plt.title('My Very Own Histogram')
plt.text(23, 45, r'$\mu=15, b=3$')
plt.show()
