"""
cleanData.py
Author: Maggie Jacoby, August 2020

This is the data cleaning function that is called when processing the env readings
Use in combination with HomeDataClasses.py and explore_env.ipynb
"""

import numpy as np
import pandas as pd
from my_functions import *


### Hard coded fill limits and threshold values
T=2  # temperature limit (more than 2 degree change)
RH=5 # relative humidity limit (more than 5% change)
L=30 # fill limit for slow modes
F=5  # fill limit for other modalities
loop_limit=12 # number of times to loop through and catch bad values


mods = {'temp_c': L, 'rh_percent': L, 'tvoc_ppb': L, 'co2eq_ppm': L, 'light_lux': F, 'dist_mm': F}


def cleanData(df, hub, mods=mods):

    for modality in mods:
        df[f'missing_{modality}'] = 0
        df.loc[df[modality].isna(), f'missing_{modality}'] = 1
        df[f'Modified_{modality}'] = 0

    df = df.asfreq(freq='10S', fill_value=np.nan)
    
    for modality in mods:
        df[modality].fillna(method='ffill', inplace=True, limit=mods[modality])
        df[modality].fillna(method='bfill', inplace=True, limit=mods[modality])
        df[f'Modified_{modality}'].fillna(1, inplace=True)
    
    df.loc[df['rh_percent'] > 100, ['rh_percent', 'Modified_rh_percent']] = [np.nan, 1]
    df['rh_percent'].fillna(method='ffill', inplace=True, limit=L)       
    
    for x in range(0, loop_limit):
        df.loc[df['temp_c'].diff() <= -T, ['temp_c', 'Modified_temp_c']] = [np.nan, 1]
        df['temp_c'].fillna(method='ffill', inplace=True, limit=L)
        
        df.loc[df['rh_percent'].diff() <= -RH, ['rh_percent', 'Modified_rh_percent']] = [np.nan, 1]
        df['rh_percent'].fillna(method='ffill', inplace=True, limit=L)

        
    for x in range(0, loop_limit):
        df.loc[df['temp_c'].diff() >= T, ['temp_c', 'Modified_temp_c']] = [np.nan, 1]
        df['temp_c'].fillna(method='ffill', inplace=True, limit=L)
        
        df.loc[df['rh_percent'].diff() >= RH, ['rh_percent', 'Modified_rh_percent']] = [np.nan, 1]
        df['rh_percent'].fillna(method='ffill', inplace=True, limit=L)


    df.loc[df['missing_temp_c'] == 1, 'Modified_temp_c'] = 1
    df.loc[df['missing_rh_percent'] == 1, 'Modified_rh_percent'] = 1

    df = df.drop(df.filter(regex='missing').columns, axis=1)
    df = df.drop(df.filter(regex='base').columns, axis=1)
    
    df['hub'].fillna(hub, inplace=True)

    return df
