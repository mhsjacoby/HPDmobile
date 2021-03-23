"""
save_as_wav.py
Author: Maggie Jacoby
"""
import os
import sys
import csv
import time
from glob import glob
import numpy as np
import pandas as pd
from datetime import datetime
import scipy.io.wavfile
import warnings
warnings.filterwarnings("ignore")

from gen_argparse import *
from my_functions import *


if __name__ == '__main__':

    for hub in hubs:
        read_root_path = os.path.join(path, hub, 'audio_csv')
        save_root_path = os.path.join(path, hub, 'audio')

        dates = glob(os.path.join(read_root_path, '2019-*'))
        for date_folder_path in sorted(dates):
            date = os.path.basename(date_folder_path)
            print(date)
            t1 = time.perf_counter()
            all_mins = sorted(mylistdir(date_folder_path))
            for minute in all_mins:
                for csv_file in sorted(glob(os.path.join(date_folder_path, minute, '*.csv'))):
                    fname = os.path.basename(csv_file).split('_')
                    new_fname = f'{fname[0]} {fname[1]}_audio.wav'

                    with open(csv_file) as csv_audio:
                        csv_reader = csv.reader(csv_audio)
                        data = []
                        for row in csv_reader:
                            data.append(int(row[0]))
                    csv_data = np.array(data, dtype=np.int32)

                    storage_folder = make_storage_directory(os.path.join(save_root_path, date, minute))
                    if len(csv_data) == 80000:
                        scipy.io.wavfile.write(os.path.join(storage_folder, new_fname), 8000, csv_data)
                    else:
                        print(f'File {fname} length is {len(csv_data)}. Wav file not written.')

            t_now = time.perf_counter()
            print(f'Time to process day is {t_now-t1}')