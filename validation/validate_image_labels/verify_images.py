"""
VerifyImages.py
Author: Maggie Jacoby

Read in image inference files along with ground truth occupancy
and find locations of false positives (ground truth = vacant, image = occupied)

=== Input ===


=== Output ===


"""


import os
import sys
import argparse
import pandas as pd

from datetime import datetime
from glob import glob

from gen_argparse import *
from my_functions import *


def get_df(path):
    df = pd.read_csv(path,index_col=0)
    df.index = pd.to_datetime(df.index)
    df["day"] = df.index.date
    df["time"] = df.index.time
    df = df[['day', 'time', 'occupied']]
    return df

def compare(gt_df, inf_df):
    inf_df.rename(columns={'occupied': 'inf'}, inplace=True)
    inf_df.drop(columns=['day', 'time'], inplace=True)
    df = pd.concat([gt_df, inf_df], axis=1, join='inner')
    df.dropna(inplace=True)
    df['inf'] = df['inf'].astype('int32')
    df['FP'] = 0
    df.loc[(df['inf'] == 1) & (df['occupied'] == 0), 'FP'] = 1
    FP_df = df.loc[df['FP'] == 1]
    FP_df = FP_df.drop(columns=['occupied', 'inf', 'day', 'time'])
    return FP_df
    

    



if __name__ == '__main__':
    # uses arguments specifed by gen_argparse.py
    print(f'List of Hubs: {hubs}')


    save_path = make_storage_directory(os.path.join(save_root, 'Summaries'))

    ground_truth_path = glob(os.path.join(path, 'Inference_DB', 'Full_inferences', f'{H_num}_occupancy.csv'))[0]
    groundTruth = get_df(ground_truth_path)


    start_end_file = 'start_end_dates.json'
    all_days = get_date_list(read_file=start_end_file, H_num=H_num)

    all_hub_fps = []
    
    for hub in hubs:
        infer_csv_path = os.path.join(path, 'Inference_DB', hub, 'img_inf', '*.csv')
        days = [day for day in sorted(glob(infer_csv_path)) if os.path.basename(day).strip('.csv') in all_days]

        if len(days) == 0:
            print(f'No days in folder: {infer_csv_path}. Exiting program.')
            sys.exit()

        print(f'Number of days: {len(days)}')
        dfs = []
        for day_path in days: 
            inf_day = get_df(day_path)

            day = os.path.basename(day_path).strip('.csv')
            day = datetime.strptime(day, '%Y-%m-%d').date()
            gt_day = groundTruth.loc[groundTruth['day'] == day]
            df = compare(gt_day, inf_day)
            dfs.append(df)
        FP_df = pd.concat(dfs, axis=0)
        FP_df.rename(columns={'FP': f'{hub}_fp'}, inplace=True)
        all_hub_fps.append(FP_df)

    all_fps = pd.concat(all_hub_fps, axis=1)
    all_fps["day"] = all_fps.index.date
    all_fps["time"] = all_fps.index.time
    print(all_fps)

    all_fps.to_csv(os.path.join(save_path, f'false_positives_{H_num}.csv'))


