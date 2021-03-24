"""
calculate_groundtruth.py
Author: Maggie Jacoby
Date: 2021-01-21

This file reads in the raw occupancy files (one per occupant) 
and generates full occuapncy profiles for the home.


=== Input ===
-path
    Where to find the data
    e.g.: /Volumes/TOSHIBA-22/H2-red/
-save (optional)
    Where to store day-wise files 
    e.g.: /Volumes/TOSHIBA-22/hpdmobile_dataset/


=== Output ===
Generates two types of files:
    
    H2_occupancy_buffer.csv (e.g.)
        Full (all days combined) occupancy profile
        has columns for each occupant 
        has final occupied column with (potential) buffer
    
    2019-03-14_H2_groundtruth.csv (e.g.)
        Day-wise occupancy profile for specified days
        only has occupied column and number
        no buffer included
"""

import os
import sys
import csv
import json
import argparse
import numpy as np
import pandas as pd
from glob import glob
from datetime import datetime, timedelta

from my_functions import *


def calculate_groundtruth_df(path):

    occupant_files = glob(f'{path}/GroundTruth/*.csv')
    occupant_names = []
    occupants = {}
    
    enter_times, exit_times = [], []

    for occ in occupant_files:
        occupant_name = os.path.basename(occ).split('-')[1].strip('.csv')
        occupant_names.append(occupant_name)
        ishome = []
        with open(occ) as csv_file:
            csv_reader, line_count = csv.reader(csv_file, delimiter=','), 0
            for row in csv_reader:
                status, when = row[1], row[2].split('at')
                dt_day = datetime.strptime(str(when[0] + when[1]), '%B %d, %Y %I:%M%p')
                ishome.append((status, dt_day))

                if line_count == 0:
                    enter_times.append(dt_day)
                line_count += 1
            exit_times.append(dt_day)
        occupants[occupant_name] = ishome

    first, last = sorted(enter_times)[0], sorted(exit_times)[-1]

    occ_range = pd.date_range(start=first, end=last, freq='10S')
    occ_df = pd.DataFrame(index=occ_range)

    for occ in occupants:
        occ_df[occ] = 99
        state1 = 'exited'

        for row in occupants[occ]:
            date = row[1]
            state2 = row[0]
            occ_df.loc[
                (occ_df.index < date) & (occ_df[occ] == 99) & 
                (state1 == 'exited') & (state2 == 'entered'), occ] = 0

            occ_df.loc[
                (occ_df.index <= date) & (occ_df[occ] == 99) & 
                (state1 == 'entered') & (state2 == 'exited'), occ] = 1
            state1 = state2

        occ_df.loc[
            (occ_df.index >= date) & (occ_df[occ] == 99) & 
            (state1 == 'exited'), occ] = 0

        occ_df.loc[
            (occ_df.index >= date) & (occ_df[occ] == 99) & 
            (state1 == 'entered'), occ] = 1

    occ_df['occupied'] = occ_df[list(occupants.keys())].max(axis=1)
    occ_df.index = pd.to_datetime(occ_df.index)
    occ_df.index.name = 'timestamp'
    # occ_df = create_buffer(occ_df)

    summary_df = occ_df.copy()
    summary_df['number'] = summary_df[list(occupants.keys())].sum(axis=1)
    summary_df = summary_df.drop(columns=list(occupants.keys()))
    
    
    return summary_df, occ_df


def create_buffer(df, buffer=5):
    num_points = buffer*6
    df['occupied'] = df['occupied'].replace(to_replace=0, value=np.nan)
    df['occupied'] = df['occupied'].fillna(method='ffill', limit=num_points)
    df['occupied'] = df['occupied'].fillna(method='bfill', limit=num_points)
    df['occupied'] = df['occupied'].fillna(value=0).astype('int32')
    return df


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Read occupancy files and generate ground truth.'
        )
    parser.add_argument(
        '-path','--path', default='', type=str, help='path of stored data.'
        )
    parser.add_argument(
        '-save', '--save', default='', type=str, help='location to save ground truth.'
        )

    args = parser.parse_args()

    path = args.path
    H_num = os.path.basename(path.strip('/')).split('-')[0]
    save_path = make_storage_directory(os.path.join(path, 'GroundTruth/GroundTruth'))

    start_end_file = 'start_end_dates.json'
    all_days = get_date_list(read_file=start_end_file, H_num=H_num)

    summary_df, occ_df = calculate_groundtruth_df(path)

    occ_save_path = make_storage_directory(os.path.join(path, 'Inference_DB/Full_inferences/'))
    occ_fname = os.path.join(occ_save_path, f'{H_num}_occupancy.csv')
    occ_df.to_csv(occ_fname, index = True)

    for day in all_days:
        day_df = summary_df.loc[day]
        fname = os.path.join(save_path, f'{day}_{H_num}_groundtruth.csv')
        day_df.to_csv(fname, index=True)