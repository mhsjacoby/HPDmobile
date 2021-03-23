"""
split_wav.py
Authors: Sin Yong Tan and Maggie Jacoby
20200-10-07
"""


import os
import sys
import argparse
import numpy as np
import pandas as pd

from glob import glob
from datetime import datetime, timedelta
from natsort import natsorted

import scipy.io.wavfile

from my_functions import *
from gen_argparse import *


samplerate = 8000






def split_wavs(path):
    date = os.path.basename(path).split(' ')[0] ############################ right here!! 
    

    minutes = mylistdir(os.path.join(path))

    for minute in minutes:

        # print('wave paths', wav_paths)
        audio_save_path = make_storage_directory(os.path.join(save_root_path, date, minute))

        wav_paths = natsorted(glob(os.path.join(path, minute, '*.wav')))
        # print('save: ', audio_save_path)
        # print(wav_paths)
        # sys.exit()

        for wav_file in wav_paths:
            # print(wave_file)
            original_fname = os.path.basename(wav_file)
            ts = original_fname.strip('_audio.wav')
            
            t1 = datetime.strptime(ts, '%Y-%m-%d %H%M%S')
            fname1 = os.path.join(audio_save_path, original_fname)

            t2 = t1 + timedelta(seconds=10)
            fname2 = os.path.join(audio_save_path, f'{t2.strftime("%Y-%m-%d %H%M%S")}_audio.wav')
            
            try:
                _, wav = scipy.io.wavfile.read(wav_file)

                wav1 = wav[:80000]
                wav2 = wav[80000:]

                scipy.io.wavfile.write(fname1, samplerate, wav1)
                scipy.io.wavfile.write(fname2, samplerate, wav2)
                # test_split(wav_file, f1, f2)

            except Exception as e:
                print(f'Error with file {original_fname}: {e}')

def test_split(orig_wav, wav1, wav2):
    _, wav = scipy.io.wavfile.read(orig_wav)
    first_val, last_val = wav[0], wav[-1]

    _, wav = scipy.io.wavfile.read(wav1)
    new_first = wav[0]

    _, wav = scipy.io.wavfile.read(wav2)
    new_last = wav[-1]

    print(f'first: {first_val}, {new_first}, diff: {first_val - new_first}')
    print(f'last: {last_val}, {new_last}, diff: {last_val - new_last}')
    print('---')


if __name__ == '__main__':

    print(f'List of Hubs: {hubs}')

    for hub in hubs:
        read_root_path = os.path.join(path, hub, 'audio_20second', '20*')
        dates = sorted(glob(read_root_path))
        dates = [x for x in dates if os.path.basename(x) >= start_date]
        save_root_path = make_storage_directory(os.path.join(save_root, hub, 'audio_split'))

        for date_folder_path in dates:
            print(f"Loading date folder: {os.path.basename(date_folder_path)} ...")
            split_wavs(date_folder_path)


        
