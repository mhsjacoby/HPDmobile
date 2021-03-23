"""
WriteSummaries.py
Author: Maggie Jacoby
Date: January 26, 2021

Calculates average completeness metrics for all homes, all hubs, all modalities
outputs final table a csv

"""

import os
import sys
import csv
import json
import argparse
import numpy as np
import pandas as pd
from glob import glob
from datetime import datetime, timedelta, time

from my_functions import *

def read_house_summary(filepath):
    df = pd.read_excel(filepath)
    df.rename(columns={'Unnamed: 0': 'date'}, inplace=True)
    df.index = df['date']
    df.drop(columns=['date'], inplace=True)
    df.fillna(0, inplace=True)
    hubs = set([x.split('_')[0] for x in list(df.columns) if x[1]=='S'])
    occ = df['Occupancy'].mean()

    mean_list = []
    for hub in sorted(hubs):
        hub_cols = [col for col in df.columns if hub in col]
        hub_df = df[hub_cols]
        hub_df.columns = hub_df.columns.str.lstrip(f'{hub}_')
        hub_mean = pd.DataFrame(hub_df.mean(axis=0)).transpose()
        hub_mean.rename(index={0: hub}, inplace=True)
        mean_list.append(hub_mean)
    summary_df = pd.concat(mean_list, axis=0)
    summary_df.index.names = ['hub']
    return summary_df, occ
    






if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Read all summaries (one per house) and combine.')
    parser.add_argument('-path','--path', default='', type=str, help='path of all house summaries.')
    parser.add_argument('-save', '--save', default='', type=str, help='location to write combined.')

    args = parser.parse_args()

    path = args.path
    save_path = args.save if len(args.save) > 0 else path
    
    homes = sorted(glob(os.path.join(path, 'H*')))

    all_homes = []

    occ_df = {}

    for home_path in homes:
        home = os.path.basename(home_path).strip('_cuonts.xlsx')
        print(home)
        home_summary, occ = read_house_summary(home_path)
        occ_df[home] = occ
        home_summary['home'] = home
        home_summary.set_index('home', append=True, inplace=True)
        home_summary = home_summary.reorder_levels(['home', 'hub'])

        all_homes.append(home_summary)
    
    full_summary = pd.concat(all_homes, axis=0)
    occupancy_df = pd.Series(occ_df)
    print(occupancy_df)
    
    # full_summary.to_csv(os.path.join(save_path, 'new_summary.csv'))

