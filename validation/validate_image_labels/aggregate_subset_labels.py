"""
aggregate_subset_labels.py
Author: Maggie Jacoby
Date: 2021-02-02
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


from my_functions import *
from gen_argparse import *

random.seed(3)


class SubsetImages():

    def __init__(self, img_folder, save_path, df_infs, num_samples=50):
        self.img_folder = img_folder
        self.save_path = save_path
        self.df_infs = df_infs
        self.num_samples = num_samples


    def get_images(self, get_func, save_loc):
        save_loc = make_storage_directory(save_loc)
        ts = get_func(self.df_infs)
        
        for t in ts:
            self.write_t(t, save_loc)
        
        df = self.df_infs.loc[ts]
        df.sort_index(inplace=True)

        return df


    def write_t(self, t, save_loc):
        ts_time = t.split(' ')[1].replace(':','')
        time_folder = f'{ts_time[0:4]}'
        path_name = os.path.join(self.img_folder, time_folder, f'*_{ts_time}_*')

        if len(glob(path_name)) > 0:
            file_src = glob(path_name)[0]
            fname = os.path.basename(file_src)
            dest = os.path.join(save_loc, fname)
            shutil.copy(file_src, dest)
        else:
            print(f'No file in {path_name}')



def get_occupied(df, num_samples=20):
    
    day_occ = df.loc[df['occupied'] == 1]
    times = day_occ.index
    sample_size = num_samples if len(times) >= num_samples else len(times)
    ts = sample(list(times), sample_size)
    all_occ_mins = set([x.split(' ')[1].replace(':','')[:4] for x in day_occ.index])
    ts_unique_mins = set([x.split(' ')[1].replace(':','')[:4] for x in ts])    
    
    return ts

def get_vacant(df, num_samples=10):

    thresh = [0, 0.1, 0.2, 0.3, 0.4, 0.5]
    ts = []
    for i, j in zip(thresh[:-1], thresh[1:]):
        day_vac = df.loc[(df['probability'] >= i) & (df['probability'] < j)]
        times = day_vac.index
        sample_size = num_samples if len(times) >= num_samples else len(times)
        t_thresh = sample(list(times), sample_size)
        ts.extend(t_thresh)

    return ts


if __name__ == '__main__':
    # uses arguments specifed by gen_argparse.py

    print(f'List of Hubs: {hubs}')
    save_root = make_storage_directory(f'/Users/maggie/Desktop')
    home_savename = make_storage_directory(os.path.join(save_root,'Auto_Labeled', H_num, 'Summaries'))

    for hub in hubs:
        hub_save = os.path.join(save_root,'Auto_Labeled', H_num, hub)
        infer_csv_path = os.path.join(path,'Inference_DB', hub, 'img_1sec', '*.csv')

        days = [day for day in sorted(glob(infer_csv_path))]

        if len(days) == 0:
            print(f'No days in folder: {infer_csv_path}. Exiting program.')
            sys.exit()

        end_date =  os.path.basename(days[-1]).strip('.csv') if not end_date else end_date
        days = [day for day in days if os.path.basename(day).strip('.csv') <= end_date]
        days = [day for day in days if os.path.basename(day).strip('.csv') >= start_date]
        
        print(f'\nHub {hub} - Number of days: {len(days)}')

        occ_hub, vac_hub = [], []

        for day in days:

            day_name = os.path.basename(day).strip('.csv')
            day_imgs = os.path.join(path, hub, img_name, day_name)

            day_infs = pd.read_csv(day, index_col='timestamp')           
            day_infs.dropna(inplace=True)
            print(f'{day_name}: {len(day_infs)} inferences')

            SI = SubsetImages(img_folder=day_imgs, save_path=hub_save, df_infs=day_infs)

            occ_save = os.path.join(hub_save, 'Occupied')
            occ_df = SI.get_images(get_func=get_occupied, save_loc=occ_save)
            occ_hub.append(occ_df)

            vac_save = os.path.join(hub_save, 'Vacant')
            vac_df = SI.get_images(get_func=get_vacant, save_loc=vac_save)
            vac_hub.append(vac_df)
            
        all_occ_images = pd.concat(occ_hub, axis=0)
        occ_fname = os.path.join(home_savename, f'{hub}_occupied.csv')
        all_occ_images.to_csv(occ_fname, index='timestamp')

        all_vac_images = pd.concat(vac_hub, axis=0)
        vac_fname = os.path.join(home_savename, f'{hub}_vacant.csv')
        all_vac_images.to_csv(vac_fname, index='timestamp')