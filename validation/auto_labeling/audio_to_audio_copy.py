"""
audio_to_audio_copy.py
Author: Maggie Jacoby
Update: 2020-10-08 change save format

Part of Labeling Workflow
- step 4 (run after manually separating )

Uses: my_functions.py

About: This code takes a file of labeled audio clips in one hub 
        and copies existing ones from another hub that match the timestamp	

=== INPUT ===
- path (where all raw audio files are stored)
- save_location (where on local machine you are storing the files to sort)
- from_hub (already sorted out)
- hubs (one or more than you want to copy)

eg: python3 audio_to_audio_copy.py -path /Volumes/TOSHIBA-21/H1-red/ -save_location /Users/maggie/Desktop/Auto-Labeled-Audio -from_hub RS4 -to_hubs RS5

==== Output ====
Audio files copied into folders for "yes" occupied
"""

import os
import sys
import argparse
import pandas as pd

from glob import glob
from natsort import natsorted

import shutil

from my_functions import *


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Description")

    parser.add_argument('-path','--path', default='', type=str, help='path of stored data') # Stop at house level, example G:\H6-black\
    parser.add_argument('-save_location', '--save', default='/Users/maggie/Desktop/Auto-Labeled-Audio', type=str, help='location to store files (if different from path')
    parser.add_argument('-from_hub', '--hub1', default="", type=str, help='hub to copy dates from... ') 
    parser.add_argument('-to_hubs', '--all_hubs',  nargs="+", default="", type=str, help='new hubs to copy... ')
    parser.add_argument('-file_type', '--audio_type', default="noise", type=str, help='audio type (eg, quiet, noise)')

    args = parser.parse_args()
    path = args.path

    save_loc = args.save
    from_hub = args.hub1

    hubs = args.all_hubs 
    audio_type = args.audio_type

    home_system = os.path.basename(path.strip('/'))
    H = home_system.split('-')
    H_num, color = H[0], H[1][0].upper()

    copy_loc = os.path.join(save_loc, home_system, audio_type, from_hub)
    
    for hub in hubs:
        print(hub)
        save_path = make_storage_directory(os.path.join(save_loc, home_system, f'{hub}_{audio_type}_auto'))

        for fname in mylistdir(copy_loc, bit='.wav'):
            day, time = fname.strip('_audio.wav').split(' ')
            minute_folder = time[:4]
            file_path = os.path.join(path, hub, 'audio', day, minute_folder, fname)
            from_loc = glob(file_path)

            if len(from_loc) > 0:
                src = from_loc[0]
                dest = os.path.join(save_path, fname)
                shutil.copy(src, dest)
            else:
                print(f'no file in: {file_path}')