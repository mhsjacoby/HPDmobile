"""
aggregate_subset_labels.py
Author: Maggie Jacoby
Date: 2021-03-16
"""


import os
import sys
import csv
import shutil
import argparse
import numpy as np
import pandas as pd
from glob import glob
from datetime import datetime, timedelta
import random
from random import sample

random.seed(1)
save_root = f'/Users/maggie/Desktop/LabeledImages'

type_info = dict(
                occupied=dict(
                            label=1, 
                            sample=150
                            ),
                vacant=dict(
                            label=0,
                            sample=60
                            )
                )


class SubsetImages():

    def __init__(self, img_folder):
        self.img_folder = img_folder

    def copy_imgs(self, ts, save_loc):
        os.makedirs(save_loc, exist_ok=True)

        for t in ts:
            path_name = self.get_time_date(t)

            if len(glob(path_name)) > 0:
                file_src = glob(path_name)[0]
                fname = os.path.basename(file_src)
                dest = os.path.join(save_loc, fname)
                shutil.copy(file_src, dest)
            else:
                print(f'No file in {path_name}')


    def get_time_date(self, t):
        ts_time = t.split(' ')[1].replace(':','')
        ts_date = t.split(' ')[0]
        time_folder = f'{ts_time[0:4]}'
        path_name = os.path.join(self.img_folder, ts_date, time_folder, f'*_{ts_time}_*')
        return path_name
    

    def sample_imgs(self, full_df, img_type):
        im, sample_size = type_info[img_type]['label'], type_info[img_type]['sample']
        df = full_df.loc[full_df['occupied'] == im]
        times = df.index
        ts = sorted(sample(list(times), sample_size))
        sampled_df = df.loc[ts]
        return sampled_df


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check zone labels for accuracy')

    parser.add_argument('-labels','--labels', default='', type=str, help='path of zone labels') 
    parser.add_argument('-drive','--drive', default='', type=str, help='path of stored images') 
    parser.add_argument('-hub', '--hub', default='', nargs='+', type=str, help='if only one hub... ')

    args = parser.parse_args()
    
    labels_path = args.labels
    H_num = os.path.basename(labels_path.strip('/'))
    img_path = glob(os.path.join('/Volumes', args.drive, f'{H_num}-*'))[0]

    if len(args.hub) > 0:
        hubs = args.hub
    else:
        hub_list = sorted(glob(os.path.join(labels_path, '*_ZONELABELS', '*_ZONELABELS')))
        hubs = [os.path.basename(hub).split('_')[1] for hub in hub_list]
    
    labeled_list = dict(occupied=[], vacant=[])
    for hub in hubs:

        days = sorted(glob(os.path.join(labels_path, '*_ZONELABELS', f'*{hub}*','*.csv')))

        if len(days) == 0:
            print(f'No days in folder: {infer_csv_path}. Exiting program.')
            sys.exit()
        print(f'\nHub {hub} - Number of days: {len(days)}')

        img_list = []
        for day in days:
            day_infs = pd.read_csv(day, index_col='timestamp')           
            day_infs.dropna(inplace=True)
            img_list.append(day_infs)

        full_img_dfs = pd.concat(img_list, axis=0)
        print(f'{len(full_img_dfs)} total infererences')
        hub_imgs = os.path.join(img_path, hub, 'img-unpickled')

        SI = SubsetImages(img_folder=hub_imgs)
        occ_samples = SI.sample_imgs(full_df=full_img_dfs, img_type='occupied')
        vac_samples = SI.sample_imgs(full_df=full_img_dfs, img_type='vacant')

        for occ, df_occ in zip(['occupied', 'vacant'], [occ_samples, vac_samples]):
            save_loc = os.path.join(save_root, H_num, occ, hub)
            ts = list(df_occ.index)
            SI.copy_imgs(ts, save_loc)
            df_occ['hub'] = hub
            labeled_list[occ].append(df_occ)
    
    for label_type in labeled_list:
        labeled_df = pd.concat(labeled_list[label_type])
        save_name = os.path.join(save_root, 'Summaries') 
        os.makedirs(save_name, exist_ok=True)
        labeled_df.to_csv(os.path.join(save_name, f'{H_num}_sampled_{label_type}.csv'), index='timestamp')