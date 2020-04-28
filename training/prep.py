import pandas as pd
import numpy as np

from training_config import columns

tags = ['parsec46', 'ng46', 'ng20', 'idle46']
tags = ['test9']
INPUT=[f'../raw_{tag}.csv' for tag in tags]
OUTPUT='./post_combined71.csv'

#  OUTPUT='./post_ng20.csv'

DO_BALANCE = 0
#  KEEP = 0.43
KEEP = 0

def combine_csv_balanced(cfs):
    min_len = min(map(len, dfs))
    ret_df = None
    for df in dfs:
        ret_df = df[:min_len] if ret_df is None else ret_df.append(df[:min_len])
    return ret_df

def combine_csv(dfs):
    ret_df = None
    for df in dfs:
        ret_df = df if ret_df is None else ret_df.append(df)
    return ret_df

def preprocess(df):
    #  df = df.loc[df.p_running.eq(0)]
    #  df = df.loc[df.throttled.eq(0)]
    df = df.loc[df.test_aggressive.eq(1)]
    df['delta_hot'] = np.where(df['delta'] < 500000, 1, 0)
    df['src_non_pref_nr'] = np.where(df['src_len'] > df['src_preferred_len'], 1, 0)
    #  df['src_non_pref_nr'] = np.where(df['src_len'] - df['src_preferred_len'] > 0, 1, 0) #/ df['src_len']).mask(df['src_len'] == 0, 0)
    df['src_non_numa_nr'] = (df['src_len'] - df['src_numa_len']) #/ df['src_len']).mask(df['src_len'] == 0, 0)
    df['extra_fails'] = np.where((df['nr_fails'] > df['cache_nice_tries']), 1, 0)
    #  df['extra_fails'] = (df['nr_fails'] - df['cache_nice_tries']) #/ df['nr_fails']).mask(df['nr_fails'] == 0, 0)
    df.src_len = df.src_len - 2
    #  df.imbalance = df.imbalance / df.src_load.mask(df.src_load.eq(0), 1)
    df.src_load = df.src_load / 1000
    df.dst_load = df.dst_load / 1000
    df.delta_faults = df.delta_faults / df.total_faults.mask(df.total_faults.eq(0), 1)
    #  df.src_load = (df.src_load / df.imbalance).mask(df.imbalance == 0, df.src_load)
    df = df[columns]
    return df

#  if type(INPUT) is not list:
#      df = preprocess(pd.read_csv(INPUT))
#      df.to_csv(OUTPUT, index=False)
#      exit()


dfs = []
for filename in INPUT:
    dfs.append(pd.read_csv(filename))

dfs = [preprocess(df) for df in dfs]
for idx, df in enumerate(dfs):
    outname = f'./post_{tags[idx]}.csv'
    print(outname)
    df.to_csv(outname, index=False)

if len(dfs) > 1:
    if DO_BALANCE:
        combined = combine_csv_balanced(dfs)
    else:
        combined = combine_csv(dfs)

    print(OUTPUT)
    combined.to_csv(OUTPUT, index=False)


"""
if POST:
    df = combine_csv(INPUT)
    df.to_csv(OUTPUT, index=False)
    exit()

#  df = combine_csv(csv_files)
if type(INPUT) is list:
    df = combine_csv_balanced(INPUT)
else:
    df = pd.read_csv(INPUT)
    if KEEP:
        if KEEP < 1:
            nrow = len(df)
            df = df[:int(nrow * KEEP)]
        else:
            df = df[:KEEP]

#  columns=['src_non_pref_nr', 'src_non_numa_nr', 'delta_hot', 'cpu_idle',
          #  'cpu_not_idle', 'cpu_newly_idle', 'same_node', 'prefer_src', 'prefer_dst',
         #  'throttled', 'p_running',
          #  'delta_faults', 'extra_fails', 'buddy_hot', 'can_migrate']


df = df.loc[df.p_running.eq(0)]
df = df.loc[df.throttled.eq(0)]

df['delta_hot'] = np.where(df['delta'] < 500000, 1, 0)
df['src_non_pref_nr'] = (df['src_len'] - df['src_preferred_len']) #/ df['src_len']).mask(df['src_len'] == 0, 0)
df['src_non_numa_nr'] = (df['src_len'] - df['src_numa_len']) #/ df['src_len']).mask(df['src_len'] == 0, 0)
df['extra_fails'] = (df['nr_fails'] - df['cache_nice_tries']) #/ df['nr_fails']).mask(df['nr_fails'] == 0, 0)
df['src_load'] = np.log10(df.src_load)
#  df.dst_load = np.log10(df.dst_load)
#  df['delta_faults'] = df['delta_faults'] #/ df['total_faults']).mask(df['total_faults'] == 0, 0)

df = df[columns]

df.to_csv(OUTPUT, index=False)
"""
