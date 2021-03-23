"""
process_count_audio.py
branch: process_noFilter
Base code written by Sin Yong Tan, based on processing technique developed by Ali Saffair, 
Helper functions stored in AudioFunctions.py
Editied and audio counting added by Maggie Jacoby
Most recent edit: 2020-12-09 
                    - Remove the filtering portion
                    - Performs mean shift, rectification, and downsampling (1/100)
                    - Saves as CSV in the same folder structure as the wav files (one csv per wav file)
"""

import os
import csv
import sys
from glob import glob
import numpy as np
import pandas as pd
from datetime import datetime

import scipy.io.wavfile
from scipy.fftpack import dct
from sklearn.preprocessing import scale

import warnings
warnings.filterwarnings("ignore")

from AudioFunctions import *
from gen_argparse import *
from my_functions import *


def process_wav(wav_name, date_folder_path, minute, fs=8000):
    wav_path = os.path.join(date_folder_path, minute, wav_name)
    t = wav_name.split(' ')[-1].strip('._audio.wav')
    time_file = f'{t[0:2]}:{t[2:4]}:{t[4:6]}'

    try:  
        _, wav = scipy.io.wavfile.read(wav_path) # _ should be same fs
        audio_len_seconds = len(wav)/fs # length of audio clip in seconds
        all_seconds.append(time_file)
        assert (audio_len_seconds == 10.0)

        len_wav = int(len(wav))
        num_final_datapoint = 800
        inc = int(len(wav)/num_final_datapoint)

        processed_audio = wav - np.mean(wav)   # Mean Shift
        processed_audio = abs(processed_audio) # Full wave rectify
        downsampled = processed_audio[0::inc]  # Downsample

        return downsampled, time_file
    
    except Exception as e:
        print(f'Error processing file {wav_path}: {e}')

        return [], time_file


# ==================================================================
## Check pi for all audio files

def check_pi(pi_path):
    found_on_pi = {}
    for day in mylistdir(pi_path, '2019-', end=False):
        pi_dir = os.path.join(pi_path, day)
        all_mins = sorted(mylistdir(pi_dir))
        if len(all_mins) == 0:
            print(f'No pi files for {day}')
        else:
            for minute in sorted(all_mins):
                this_minute = mylistdir(os.path.join(pi_dir, minute), bit='.wav')
                for audio_f in this_minute:
                    name = audio_f.split('_')[0]
                    found_on_pi[name] = (day, minute)
    return found_on_pi
# ==================================================================


if __name__ == '__main__':

    for hub in hubs:

        read_root_path = os.path.join(path, hub, 'audio')
        pi_path = os.path.join(path, hub, 'audio_from_pi')
        save_root_path = os.path.join(save_root, hub, 'processed_audio')

        print(f'Home: {home_system}, hub: {hub}, pi_audio: {pi_audio}, read_root: {read_root_path}')

        dates = glob(os.path.join(read_root_path, '2019-*'))
        if len(start_date) > 0:
            dates = [x for x in dates if os.path.basename(x) >= start_date]
        if len(end_date) > 0:
            dates = [x for x in dates if os.path.basename(x) <= end_date]
        print('dates: ', [os.path.basename(date) for date in dates])

        all_days_data = {}

        if pi_audio == True:
            print('Checking pi ...')
            found_on_pi = check_pi(pi_path)
            print(f'Number of files found on pi: {len(found_on_pi)}')
        else:
            print('No pi audio files received')
            found_on_pi = []

        start = datetime.now()
        # ==== Start Looping Folders ====

        for date_folder_path in dates:

            date = os.path.basename(date_folder_path)
            start = datetime.now()
            print("Loading date folder: " + date + "...")
            all_mins = sorted(mylistdir(date_folder_path))
            
            all_wavs = glob(os.path.join(date_folder_path, '*', '*.wav'))
            print(date, len(all_mins), len(all_wavs))

            all_seconds = []

            if len(all_mins) > 0:                 
                hours = [str(x).zfill(2) + '00' for x in range(0,24)]

                for hour in hours:

                    # create dictionaries to store downsampled (*_ds) audio
                    content_ds = {}
                    full_list = make_all_seconds(hour)
                    this_hour = [x for x in all_mins if x[0:2]==hour[0:2]]

    

                    for minute in sorted(this_hour):

                        minute_path = os.path.join(date_folder_path, minute)
                        wavs = sorted(mylistdir(minute_path, bit='.wav'))

                        if len(wavs) > 0:
                            for wav_name in wavs:
                                save_path = make_storage_directory(os.path.join(save_root_path, 'audio_csv', date, minute))
                                fname = wav_name.strip('_audio.wav').replace(' ', '_') + f'_{hub}_{H_num}.csv'
                                
                                downsampled_audio, time_file = process_wav(wav_name, date_folder_path, minute)

                                if len(downsampled_audio) > 0:
                                    np.savetxt(os.path.join(save_path, fname), downsampled_audio, delimiter=",")
                                    all_seconds.append(time_file)
                                    content_ds[time_file] = downsampled_audio # store downsampled

                    ### Check for missing files on pi and read in
                    list_hour_actual = [x for x in content_ds.keys()]

                    missing = list(set(full_list)-set(list_hour_actual))
                    missing = [f'{date} {x.replace(":", "")}' for x in missing]

                    if len(missing) > 0:
                        if len(found_on_pi) > 0:
                            this_hour_on_pi = [x for x in found_on_pi if (x.split(' ')[0] == date and x.split(' ')[1][0:2] == hour[0:2])]
                            for m in missing:
                                if m in this_hour_on_pi:
                                    day, minute = found_on_pi[m]
                                    downsampled_pi, time_file = process_wav(f'{m}_audio.wav', os.path.join(pi_path, day), minute)

                    
                    ################ npz_compressed saving at the end of each hour (or desired saving interval) ################
                    # fname_ds = f'{date}_{hour}_{hub}_{H_num}_ds.npz' # ==> intended to produce "0000", "0100", .....
                    # fname_csv = f'{date}_{hour}_{hub}_{H_num}.csv'
                    # downsampled_save_path = os.path.join(downsampled_folder, fname_ds)
                    # np.savez_compressed(downsampled_save_path, **full_content_ds)
                    ################################################################
            end = datetime.now()
            print(f'Time to process day {date}: {str(end-start).split(".")[0]}.')

