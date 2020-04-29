import pandas as pd
import sys

#  df = pd.read_csv('cmdata.csv')
#  df = pd.read_csv('./parsec_2.csv', index_col='ts')
#  df = pd.read_csv('./test_running.csv', index_col='ts')
filename = sys.argv[1]
df = pd.read_csv(filename, index_col='ts')
#  print(df['can_migrate'].eq(1).sum(), df['can_migrate'].eq(0).sum())

#  sel = df.loc[(df['prefer_dst'] == 0) & (df['prefer_src'] == 0) & (df['same_node'] == 0)]
#  sel = df.loc[df['same_node'] == 0]
#  sel = df[df.throttled.eq(1) & df.can_migrate.eq(1)]
#  sel = df[df.fair_class.eq(0)]

#  A = (df['can_migrate'] == 0).sum()
#  B = (df['can_migrate'] == 1).sum()
#  print(A, B, A/B)
print(filename)
total = len(df)
stats = {}
stats['throttled and can_migrate'] = (df.throttled.eq(1) & df.can_migrate.eq(1)).sum()
stats['throttled'] = df.throttled.eq(1).sum()
stats['running'] = df.p_running.eq(1).sum()
stats['running and can_migrate'] = (df.p_running.eq(1) & df.can_migrate.eq(1)).sum()
stats['buddy_hot and can_migrate'] = (df.buddy_hot.eq(1) & df.can_migrate.eq(1)).sum()
stats['throttled and running'] = (df.throttled.eq(1) & df.p_running.eq(1)).sum()
stats['throttled and aggressive'] = (df.throttled.eq(1) & df.test_aggressive.eq(1)).sum()
stats['running and aggressive'] = (df.p_running.eq(1) & df.test_aggressive.eq(1)).sum()
stats['!test_aggressive and can_migrate'] = (df.test_aggressive.eq(0) & df.can_migrate.eq(1)).sum()
stats['mean load'] = df.src_load.max()
stats['mean dstload'] = df.dst_load.mean()
stats['mean len'] = df.src_len.mean()
stats['test_aggressive'] = df.test_aggressive.eq(1).sum()
#  stats['fair_class'] = df.fair_class.eq(1).sum()
stats['can migrate'] = df.can_migrate.eq(1).sum()
stats['total'] = len(df)
for item in stats:
    print(item, stats[item], '{:.4f}'.format(stats[item] / total))

pd.set_option('display.max_rows', df.shape[0]+1)

#  #  print(sel.loc[:, ['ts', 'pid', 'src_cpu', 'dst_cpu', 'delta_faults', 'can_migrate']])
#  print(sel)
#  print(len(sel))
#  sel = df[df['delta_faults'].ne(0) & df['prefer_src'].eq(0) & df['prefer_dst'].eq(0)]
#  sel = df[df['prefer_src'].eq(0) & df['prefer_dst'].eq(0)]
#  print(sel[['prefer_src', 'prefer_dst', 'delta', 'delta_faults', 'can_migrate', 'src_numa_len']])
