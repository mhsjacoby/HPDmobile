"""
count_all_modalities.py
Author: Maggie Jacoby
date: 2021-01-13

"""

import os
import csv
import sys
from glob import glob
import numpy as np
import pandas as pd
from datetime import datetime

from gen_argparse import *
from my_functions import *



def count_audio(days_to_use, data_path, hub=None, max_files=8640):
    print(f'Counting audio on {hub}...')
    dates = glob(os.path.join(data_path, '2019-*'))
    dates = [f for f in dates if os.path.basename(f) in days_to_use]

    counts = {}
    for day in dates:
        all_times = glob(os.path.join(day, '*/*.csv'))
        set_times = set([os.path.basename(x).split('_')[1] for x in all_times])
        dt = datetime.strptime(os.path.basename(day), '%Y-%m-%d').date()
        totals = len(set_times)/max_files
        counts[dt] = float(f'{totals:.2}') if totals != 0 else 0.0

    return counts


def count_images(days_to_use, data_path, hub=None, max_files=86400):
    print(f'Counting images on {hub}...')
    dates = glob(os.path.join(data_path, '2019-*'))
    dates = [f for f in dates if os.path.basename(f) in days_to_use]
    print('num days: ', len(dates))

    counts = {}
    for day in dates:
        all_times = glob(os.path.join(day, '*/*.png'))
        set_times = set([os.path.basename(x).split('_')[1] for x in all_times])
        dt = datetime.strptime(os.path.basename(day), '%Y-%m-%d').date()
        totals = len(set_times)/max_files
        counts[dt] = float(f'{totals:.2}') if totals != 0 else 0.0

    return counts

def count_dark(days_to_use, data_path, hub, max_files=86400):
    print(f'Counting dark images on {hub}...')
    data_path = os.path.join(data_path, f'{H_num}_{hub}_DARKIMAGES')
    dates = glob(os.path.join(data_path, '2019-*'))
    dates = [f for f in dates if os.path.basename(f).split('_')[0] in days_to_use]
    counts = {}
    for day in dates:
        all_times = pd.read_csv(day)
        all_times = all_times.values.tolist()
        set_times = set([x[0].split(' ')[1] for x in all_times])
        dt = datetime.strptime(os.path.basename(day).split('_')[0], '%Y-%m-%d').date()
        totals = len(set_times)/max_files
        counts[dt] = float(f'{totals:.2}') if totals != 0 else 0.0

    return counts


def count_env(days_to_use, data_path, hub=None, max_seconds=8640):
    print(f'Counting environmental on {hub}...')
    dates = glob(os.path.join(data_path, '*_2019-*'))
    dates = [f for f in dates if os.path.basename(f).split('_')[2].strip('.csv') in days_to_use]

    counts = {}
    for day in dates:
        cols_to_read = ['timestamp', 'tvoc_ppb', 'temp_c', 'rh_percent', 'light_lux', 'co2eq_ppm', 'dist_mm']
        day_data = pd.read_csv(day, usecols=cols_to_read, index_col='timestamp')
        # complete_data = day_data.dropna(axis=0, how='all')
        complete_data = day_data.dropna(axis=0, how='any')
        dt = datetime.strptime(os.path.basename(day).split('_')[2].strip('.csv'), '%Y-%m-%d').date()
        totals = len(complete_data)/max_seconds
        counts[dt] = float(f'{totals:.2}') if totals != 0 else 0.0

    return counts

def count_occ(days_to_use, data_path, max_seconds=8640):
    
    dates = glob(os.path.join(data_path, '*_groundtruth.csv'))
    dates = [f for f in dates if os.path.basename(f).split('_')[0] in days_to_use]
    print(f'Counting occupancy for {len(dates)} days')

    counts = {}
    for day in dates:
        cols_to_read = ['timestamp', 'occupied']
        day_data = pd.read_csv(day, usecols=cols_to_read, index_col='timestamp')
        dt = datetime.strptime(os.path.basename(day).split('_')[0], '%Y-%m-%d').date()
        occ_df = day_data.loc[day_data.occupied == 1]
        totals = len(occ_df)/max_seconds
        counts[dt] = float(f'{totals:.2}') if totals != 0 else 0.0

    occ_counts = {'Occupancy': counts}
    occ_counts_df = pd.DataFrame(occ_counts)    
    print(occ_counts_df)

    return occ_counts_df





def get_count_df(mod_name, mod_lookup, sub_path=None):
    counts = {}
    for hub in hubs[:]:
        if sub_path:
            data_path = os.path.join(path, hub, sub_path)
        else:
            data_path = os.path.join(path, hub)
        counts[f'{hub}_{mod_name}'] = mod_lookup(days_to_use=all_days, data_path=data_path, hub=hub)
    df = pd.DataFrame(counts)
    print(df)
    return df




if __name__ == '__main__':

    # dbDays = database_days()[H_num]
    start_end_file = 'start_end_dates.json'
    all_days = get_date_list(read_file=start_end_file, H_num=H_num)
    
    print(f'{H_num}: {len(all_days)} days')    

    occ_path = os.path.join(path, 'GroundTruth/GroundTruth')
    occ_counts = count_occ(days_to_use=all_days, data_path=occ_path)

    env_counts = get_count_df(sub_path='processed_env/CSV-raw', mod_name='Env', mod_lookup=count_env)
    audio_counts = get_count_df(sub_path='processed_audio/audio_csv', mod_name='Audio', mod_lookup=count_audio)
    image_counts = get_count_df(sub_path='img-unpickled', mod_name='Img', mod_lookup=count_images)

    dark_counts = get_count_df(mod_name='Img_dark', mod_lookup=count_dark)
    print('Done counting.')

    combined_img = pd.DataFrame()
    for col1, col2 in zip(sorted(image_counts.columns), sorted(dark_counts.columns)):
        if col1.split('_')[0] != col2.split('_')[0]:
            print(f'mismatch! Can not combine {col1} and {col2}')
            continue
        combined_img[col1] = image_counts[col1] + dark_counts[col2]

    # env_counts.to_csv('~/Desktop/env_df_counts.csv')
    # image_counts.to_csv('~/Desktop/image_df_counts.csv')
    # audio_counts.to_csv('~/Desktop/audio_df_counts.csv')
    # dark_counts.to_csv('~/Desktop/dark_df_counts.csv')


    full_counts = pd.concat([audio_counts, dark_counts, combined_img, env_counts, occ_counts], axis=1)
    full_counts = full_counts.reindex(sorted(full_counts.columns), axis=1)
    full_counts = full_counts.sort_index()
    print(full_counts.index)

    full_counts.to_excel(f'~/Desktop/CompleteSummaries/new_summary_code/{H_num}_counts.xlsx')
