import pandas as pd

filename = './post_ng46.csv'
df = pd.read_csv(filename)

print(filename)
total = len(df)
stats = {}
#  stats['throttled and can_migrate'] = (df.throttled.eq(1) & df.can_migrate.eq(1)).sum()
#  stats['throttled'] = df.throttled.eq(1).sum()
#  stats['running'] = df.p_running.eq(1).sum()
#  stats['running and can_migrate'] = (df.p_running.eq(1) & df.can_migrate.eq(1)).sum()
stats['buddy_hot and can_migrate'] = (df.buddy_hot.eq(1) & df.can_migrate.eq(1)).sum()
stats['delta_hot and can_migrate | delta_hot'] = (df.delta_hot.eq(1) & df.can_migrate.eq(1)).sum() / df.delta_hot.eq(1).sum()
stats['mean srcload'] = df.src_load.mean()
stats['mean dstload'] = df.dst_load.mean()
stats['mean len'] = df.src_len.mean()
stats['mean dstlen'] = df.dst_len.mean()
stats['can migrate'] = df.can_migrate.eq(1).sum()
#  stats['0 src_load'] = df.src_load.eq(0).sum()
stats['long q'] = df.src_len.gt(0).sum()
stats['long dstq'] = df.dst_len.gt(0).sum()

stats['total'] = len(df)
for item in stats:
    print(item, stats[item], '{:.4f}'.format(stats[item] / total))

pd.set_option('display.max_rows', df.shape[0]+1)

#  print(df.src_len)

#  print(sel)
#  print(len(sel))
#  sel = df[df['delta_faults'].ne(0) & df['prefer_src'].eq(0) & df['prefer_dst'].eq(0)]
#  sel = df[df['prefer_src'].eq(0) & df['prefer_dst'].eq(0)]
#  print(sel[['prefer_src', 'prefer_dst', 'delta', 'delta_faults', 'can_migrate', 'src_numa_len']])
