"""
acc_at_all_thresholds.py
Authors: Maggie Jacoby  and  Sin Yong Tan
date: 3-30-2021
"""

import os
import sys
import csv
import shutil
# import argparse
import numpy as np
import pandas as pd
from glob import glob
from datetime import datetime, timedelta
import random
from random import sample

from sklearn.metrics import accuracy_score, confusion_matrix, classification_report


def get_gt_images(home, image_type, occ_val):

    images = sorted(glob(os.path.join(images_path, home, image_type, f'*_{home}.png')))
    print(f'{image_type} images: ', len(images))
    image_names = [os.path.basename(x).strip('.png') for x in images]
    name_tuples = [x.split('_') for x in image_names]
    
    img_dict = []
    for t in name_tuples:
        ts = datetime.strptime(f'{t[0]}_{t[1]}', '%Y-%m-%d_%H%M%S')
        img_dict.append(dict(timestamp=ts, hub=t[2], home=t[3]))

    img_df = pd.DataFrame(img_dict)
    img_df['ground truth'] = occ_val
    img_df.index = img_df['timestamp']
    img_df.drop(columns=['timestamp'], inplace=True)

    return img_df


def get_metrics(p, n, fp, fn):

    tp = p-fn
    tn = n-fp

    acc = (tp+tn)/(p+n)
    TPR = tp/(tp+fn) if tp+fn > 0 else 0.0
    TNR = tn/(tn+fp) if tn+fp > 0 else 0.0

    return {'accuracy': acc, 'TPR': TPR, 'TNR': TNR}


def metric_evals(df, th_step=0.05):
    thresh_range = np.arange(0.05, 0.9, th_step)
    metrics = ['accuracy', 'TPR', 'TNR']

    occ = df.loc[df['ground truth'] == 1]
    vac = df.loc[df['ground truth'] == 0]

    th_dict = {x:[] for x in metrics}
    col_names = []
    for x in thresh_range:
        col_names.append(f'{x:.2}')

        pred_occ = df.loc[df['probability'] > x]
        pred_vac = df.loc[df['probability'] <= x]

        fp = len(pred_occ.loc[pred_occ['ground truth'] == 0])
        fn = len(pred_vac.loc[pred_vac['ground truth'] == 1])
        p, n = len(occ), len(vac)

        thresh_metrics = get_metrics(p=p, n=n, fp=fp, fn=fn)
        for key, value in thresh_metrics.items():
            th_dict[key].append(f'{value:.2}')

    metrics_df = pd.DataFrame.from_dict(data=th_dict, orient='index', columns=col_names)
    return metrics_df


infs_path = '/Users/maggie/Desktop/InferenceDB'
images_path = '/Users/maggie/Desktop/V2_V3_images'

if __name__ == '__main__':

    homes = sorted(glob(os.path.join(infs_path, 'H*')))
    homes = [os.path.basename(x).split('-')[0] for x in homes]

    for H_num in homes:
        print(H_num)

        vac_df = get_gt_images(home=H_num, image_type='vacant', occ_val=0)
        img_df = get_gt_images(home=H_num, image_type='occupied', occ_val=1)
        df = pd.concat([vac_df, img_df], axis=0)

        hubs = sorted(vac_df['hub'].unique())

        all_hubs = []
        total_metrics = []
        all_merged = []

        for hub in hubs:
            print(hub)
            inf_dfs = []
            hub_df = df.loc[df['hub'] == hub]
            # unique_days = sorted(set(hub_df.index.date))

            for day in glob(os.path.join(infs_path, f'{H_num}-*', hub, 'img_1sec', '*.csv')):
                inf_dfs.append(pd.read_csv(day, index_col='timestamp', usecols=['timestamp', 'probability']))
            inf_hub_df = pd.concat(inf_dfs, axis=0)
            inf_hub_df = inf_hub_df.sort_index()
            inf_hub_df.index = pd.to_datetime(inf_hub_df.index)

            merged_df = hub_df.join(inf_hub_df, how='left')
            all_merged.append(merged_df)

            hub_metrics = metric_evals(df=merged_df)
            hub_metrics['hub'] = hub
            total_metrics.append(hub_metrics)

        all_df = pd.concat(all_merged, axis=0)
        all_metrics = metric_evals(df=all_df)
        all_metrics['hub'] = 'all'

        total_metrics.append(all_metrics)
        total_df = pd.concat(total_metrics, axis=0)

        total_df.index = [total_df['hub'], total_df.index]
        total_df.drop(columns=['hub'], inplace=True)
        total_df.to_csv(f'/Users/maggie/Desktop/{H_num}_thresholds_all_values.csv')

