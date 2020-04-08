import pandas as pd
import numpy as np
import random


def random_stratify(src_df, label):
    nrow = len(src_df)
    classes = [0, 1]
    c_cnt = {}
    for c in classes:
        c_cnt[c] = src_df[label].eq(c).sum()
    c = sorted(c_cnt, key=c_cnt.get)[0]
    sel_cnt = c_cnt[c]
    sel_df = src_df[src_df[label].eq(c)]
    classes.remove(c)
    for c in classes:
        c_idx = src_df[src_df[label].eq(c)].index
        sel_df = sel_df.append(src_df.iloc[random.sample(list(c_idx), k=sel_cnt)])
    return sel_df


TAG = 'combined'
INPUT = './post_' + TAG + '.csv'
df = pd.read_csv(INPUT)
df = random_stratify(df, 'can_migrate')
df.to_csv('post_' + TAG + '_stratified.csv', index=False)
