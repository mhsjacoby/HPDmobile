"""
validate_img_labels.py
Author: Maggie Jacoby
Date: 2021-03-18
"""

import os
import sys
import csv
import yaml
import pickle
import logging
import argparse
import numpy as np
import pandas as pd
from glob import glob
from datetime import datetime, date


def get_difference(df, title, val):
    predicted = df.loc[(df['hub'] == hub) & (df['occupied'] == val)]
    predicted = predicted.sort_index()
    predicted.index = pd.to_datetime(predicted.index)

    original_images = sorted(glob(os.path.join(home, title, hub, f'*_{hub}_{H_num}.png')))
    missclassified = sorted(glob(os.path.join(home, f'*_to_{title}', f'*_{hub}_{H_num}.png')))
    images = original_images + missclassified

    img_times = [(os.path.basename(f).split('_')[:2]) for f in images]
    img_times = [datetime.strptime(f'{f[0]}_{f[1]}', '%Y-%m-%d_%H%M%S') for f in img_times]
    
    actual = pd.DataFrame(val, index=img_times, columns=['ground truth'])

    return missclassified, actual, predicted


def get_metrics(p, n, fp, fn):

    tp = p-fn
    tn = n-fp

    acc = (tp+tn)/(p+n)
    f1 = tp/(tp+0.5*(fp+fn)) if tp+fp+fn > 0 else 0.0
    f1_rev = tn/(tn+0.5*(fp+fn)) if tn+fp+fn > 0 else 0.0

    TPR = tp/(tp+fn) if tp+fn > 0 else 0.0
    FPR = fp/(tn+fp) if tn+fp > 0 else 0.0

    TNR = tn/(tn+fp) if tn+fp > 0 else 0.0
    FNR = fn/(tp+fn) if tp+fn > 0 else 0.0

    return {'accuracy': acc, 'TPR': TPR, 'TNR': TNR, 'FPR': FPR, 'FNR': FNR,  
            'f1': f1, 'f1_rev': f1_rev, 'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn,
            'occ': p, 'vac': n, 'total': p+n}


# path = '/Users/maggie/Desktop/ImageLabeling/LabeledImages_20perc'
path = '/Users/maggie/Desktop/LabeledImages/3-30'

labels = os.path.join(path, 'Summaries', 'AsLabeled')
homes = sorted(glob(os.path.join(path, 'H*')))

mean_hubs = {}

for home in homes:
    H_num = os.path.basename(home)

    pred_occ = pd.read_csv(os.path.join(labels, f'{H_num}_sampled_occupied.csv'), index_col='timestamp')
    pred_vac = pd.read_csv(os.path.join(labels, f'{H_num}_sampled_vacant.csv'), index_col='timestamp')
    all_preds = pd.concat([pred_occ, pred_vac], axis=0)

    hubs = sorted(glob(os.path.join(home, 'vacant/*S*')))
    hubs = [os.path.basename(h) for h in hubs]
    hubs_summary = {}
    all_P, all_N, all_fp, all_fn = 0,0,0,0
    for hub in hubs:

        FN, P, predicted_occ = get_difference(df=all_preds, title='occupied', val=1)
        FP, N, predicted_vac = get_difference(df=all_preds, title='vacant', val=0)

        full_df = pd.concat([predicted_occ, predicted_vac], axis=0)
        full_df.rename({'occupied':'predicted'}, axis='columns', inplace=True)
        full_df['actual'] = 0
        full_df.loc[full_df.index.isin(P.index), 'actual'] = 1  
        full_df = full_df.sort_index()

        
        save_path = os.path.join(path, 'Summaries', 'TrueLabels', H_num)
        os.makedirs(save_path, exist_ok=True)
        full_df.drop(columns=['hub'], inplace=True)
        # print(full_df)
        full_df.to_csv(os.path.join(save_path, f'{H_num}_{hub}_zone_groundtruth.csv'), index='timestamp')
        hubs_summary[hub] = get_metrics(p=len(P), n=len(N), fp=len(FP), fn=len(FN))
        all_P += len(P)
        all_N += len(N)
        all_fp += len(FP)
        all_fn += len(FN)
        

    hubs_summary['all'] = get_metrics(p=all_P, n=all_N, fp=all_fp, fn=all_fn)

    summary_df = pd.DataFrame(hubs_summary)
    # print(summary_df)
    mean_hubs[H_num] = summary_df['all']
    # print(summary_df['all'])
    # sys.exit()
    summary_df = summary_df.transpose()
    summary_df['home'] = H_num
    summary_df.index.name = 'hub'
    summary_df.set_index('home', append=True, inplace=True)
    summary_df = summary_df.reorder_levels(['home', 'hub'])
    # print(summary_df.loc['all'])
    summary_df.to_csv(os.path.join(path, 'Summaries', f'{H_num}_metrics.csv'), index='home')
#     mean_hubs[H_num] = hubs_summary.loc[hubs_summary['hub'] == 'all']
#     # mean_hubs[H_num] = summary_df.mean(axis=0)

mean_df = pd.DataFrame(mean_hubs)
# print(mean_df)
mean_df.to_csv(os.path.join(path, 'Summaries', 'complete_metrics.csv'), index='hub')

