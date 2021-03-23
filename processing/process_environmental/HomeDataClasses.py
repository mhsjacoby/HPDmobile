"""
HomeDataClasses.py
Maggie Jacoby
updated: August 25, 2020 - remove parent class "HomeData"
import into env data cleaning jupyter notebook
"""


import os
import sys
import csv
import ast
import json
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

from my_functions import *

from cleanData import *

class ReadEnv():
    
    def __init__(self, house_entry, sensor_hubs = [], pi=True, root_dir='/Users/maggie/Desktop/HPD_mobile_data/HPD-env', write=True):
        self.home, self.system = house_entry.split('-')
        # self.path = f'{root_dir}/{house_entry}' if root_dir.strip('/').split('/')[0] == 'Volumes' else f'{root_dir}/HPD_mobile-{self.home}/{house_entry}'
        self.path = root_dir
        self.summary_dir = make_storage_directory(os.path.join(self.path, 'Summaries', 'EnvSummaries'))
        self.hubs = sorted(sensor_hubs if len(sensor_hubs) > 0 else mylistdir(self.path, bit=f'{self.system[0].upper()}S', end=False))
        self.pi = pi
        self.day_length = 8640
        self.write = write


    def read_in_data(self, path, measurements):
        with open(path, 'r') as f:
            try:
                data_dicts = json.loads(f.read())
                for time_point in data_dicts:
                    for measure in time_point:
                        measurements[measure].append(time_point[measure])
            except Exception as e:
                pass
            return measurements

    def read_all(self, path, days):
        print(f'> reading in data from: {path}')
        measurements = {
            'time':[], 'tvoc_ppb':[], 'temp_c':[], 'rh_percent':[], 
            'light_lux':[],'co2eq_ppm':[], 'dist_mm':[], 'co2eq_base':[], 'tvoc_base':[]}
        for day in days:
            all_mins = sorted(mylistdir(os.path.join(path, day)))
            for m in all_mins:
                files = sorted(mylistdir(os.path.join(path, day, m), '.json'))
                for f in files:
                    measurements = self.read_in_data(os.path.join(path, day, m, f), measurements)
        df = pd.DataFrame.from_dict(measurements)
        return df
            
        
    def get_all_data(self, hub):
        env_dir = os.path.join(self.path, hub, 'env_params')
        main_days = sorted(mylistdir(env_dir))
        df = self.read_all(env_dir, main_days)
        df = self.clean_dates(df)
        if self.pi:
            print(f'> gathering data from pi...')
            from_pi = os.path.join(self.path, hub, 'env_from_pi') 
            pi_days = sorted(mylistdir(from_pi))
            pi_df = self.read_all(from_pi, pi_days)
            pi_df = self.clean_dates(pi_df)
            df = df.append(pi_df)
        df['timestamp'] = df.index
        df['hub'] = hub
        df = df.drop_duplicates(subset=['timestamp']).set_index('timestamp').sort_index()
        return df
    
    
    def clean_dates(self, df): 
        print(f'> cleaning dates on df of length: {len(df)}')
        df['time'] = df['time'].str.strip('Z').str.replace('T',' ')
        df['timestamp'] = pd.to_datetime(df['time'])
        df = df.drop(columns = ['time'])
        df = df.set_index('timestamp')
        df.index = df.index.round('10s')
        df.fillna(np.nan)
        return df


        
    def make_day_dfs(self, df, hub, write_day=True, summary_name='data-summary', method='raw'):
        print(f'> Splitting by day... ')
        dates = sorted(list(set([d.strftime('%Y-%m-%d') for d in df.index])))
        day_lens = {}
        counts = {}
        for day in dates:
            day_df = df.loc[day:day]
            day_lens[day] = len(day_df)
            counts[day] = day_df.notnull().sum().to_dict()
            self.write_data(day_df, hub, name=f'{self.home}_{hub}_{day}', folder_name=f'processed_env/CSV-{method}') if write_day else print(f'not writing {method} data for day {day}')
        self.write_summary(hub, day_lens, counts, summary_name)
    
    #folder_name is UNDER the hub (eg 'cleaned_CSV'), storage_path is ABOVE the hub (eg '/Users/maggie/Desktop/all_cleaned_dfs')
    def write_data(self, df_to_write, hub, name, storage_path=None, folder_name='processed_env' ):
        storage_path = self.path if not storage_path else storage_path
        storage_dir = make_storage_directory(os.path.join(storage_path, hub, folder_name))
        target_fname = os.path.join(storage_dir, f'{name}.csv')
        df_to_write.to_csv(target_fname, index_label = 'timestamp', index = True)
        print(f'writing: {target_fname}')
                             

    def write_summary(self, hub, dates, counts, name):
        fname = os.path.join(self.summary_dir, f'{self.home}-{hub}-{name}.txt')
        with open(fname, 'w+') as writer:
            writer.write(f'Hx Hub Date       %    {[mod for mod in mods]} \n')
            for day in dates:
                percent = f'{dates[day]/self.day_length:.2f}' if self.day_length != 0 else 0.00
                c = [float(f'{counts[day][x]/self.day_length:.2f}') for x in mods] if percent else percent
                details = f'{self.home} {hub} {day} {percent} {c}'
                writer.write(details + '\n')
        writer.close()
        print(f'{fname} : Write Sucessful!')


    def clean_data(self, full_df=None, write=True):
        print(f'*********** Cleaning data *********** ')
        full_df = self.full_df if not full_df else full_df
        dfs = {}
        for hub in full_df['hub'].unique():
            print(f'> Cleaning data for hub: {hub}')
            df = full_df.loc[full_df['hub'] == hub].copy()      
            df = cleanData(df, hub)                          # cleanData function import from cleanData.py
            dfs[hub] = df
            self.write_data(df, hub, name=f'{self.home}_{hub}_full_cleaned') if write else print('not writing cleaned data.')
            self.make_day_dfs(df, hub, summary_name='data-summary-cleaned', method='cleaned')

        all_dfs_cleaned = [dfs[hub] for hub in dfs]
        self.full_cleaned = pd.concat(all_dfs_cleaned)
        self.full_cleaned['time'] = self.full_cleaned.index




    def main(self):
        self.all_dfs = {}
        print('hubs: ', self.hubs)
        for hub in self.hubs:
            print(f'\n> working on: {self.home}-{self.system}, hub: {hub}')
            # sys.exit()
            hub_df = self.get_all_data(hub)
            self.write_data(hub_df, hub, name=f'{self.home}_{hub}_all_raw') if self.write else print('not writing raw data.')
            self.make_day_dfs(hub_df, hub, write_day=True)    # doesn't return anything, just write the (CSVs and) summaries by day (write=True to write CSVs)
            self.all_dfs[hub] = hub_df        # stores in a dict by hub
        all_hubs = [self.all_dfs[hub] for hub in self.hubs]
        self.full_df = pd.concat(all_hubs)
            



