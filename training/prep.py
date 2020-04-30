import pandas as pd
import numpy as np

from training_config import columns, OLD_KERNEL


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


def _preprocess(df):
    if OLD_KERNEL:
        df = df.loc[df.p_running.eq(0)]
        df = df.loc[df.throttled.eq(0)]
    else:
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


def preprocess(tags, balance=False, out_tag=None):
    out_tag = out_tag or 'default'
    output = f'./post_{out_tag}.csv'
    input_list=[f'../raw_{tag}.csv' for tag in tags]
    dfs = []
    for filename in input_list:
        dfs.append(pd.read_csv(filename))

    dfs = [_preprocess(df) for df in dfs]
    for idx, df in enumerate(dfs):
        outname = f'./post_{tags[idx]}.csv'
        print('Outputing ', outname)
        df.to_csv(outname, index=False)

    if len(dfs) > 1:
        if balance:
            combined = combine_csv_balanced(dfs)
        else:
            combined = combine_csv(dfs)

        print('Combined output', output)
        combined.to_csv(output, index=False)


if __name__ == '__main__':
    tags = ['parsec46', 'ng46', 'ng20', 'idle46']
    tags = ['test9']
    out_tag = 'combined71'

    DO_BALANCE = 0
    #  KEEP = 0.43
    KEEP = 0

    preprocess(tags, DO_BALANCE, out_tag)
