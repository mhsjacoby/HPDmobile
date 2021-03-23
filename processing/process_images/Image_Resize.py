"""
Image_Resize.py
Maggie Jacoby
created 03/22/2020
Updated: 2021-01-05 : Strip down code. Remov functions and summary writing

This class takes the images that were unpickled to 112x112 size and further 
downsizes them to 32x32 for the public database
"""

import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime
from PIL import Image
import json
from glob import glob


from my_functions import *
from gen_argparse import *

class ImageFile():
    def __init__(self, sensor, files_dir, house, write_loc, start_date, end_date, img_name, home_system, img_sz=32):
        self.sensor = sensor
        self.original_loc = files_dir   
        self.home = house
        self.system = home_system
        self.img_sz = img_sz
        self.write_path = write_loc
        self.start_date = start_date
        self.end_date = end_date
        self.img_name = img_name
        self.get_params()  
        self.total_per_day = 86400


    def get_params(self):
        self.path = os.path.join(self.original_loc, self.sensor, self.img_name)
        self.write_location = make_storage_directory(os.path.join(self.write_path, self.sensor, f'img-downsized-{self.img_sz}'))
                

    def main(self):
        all_days = sorted(mylistdir(self.path, '2019-', end=False))
        print('total files:', len(all_days))
        all_days = [day for day in all_days if day >= self.start_date]
        all_days = [day for day in all_days if day <= self.end_date]
        print('files to downsize:', len(all_days))
        print(all_days)

        sensor = self.sensor
        home = self.home
        path = self.path
        write_location = self.write_location
        img_sz = self.img_sz

        open_im = Image.open
        bil = Image.BILINEAR



        for day in all_days:
            start = datetime.now()
            F = 0
            print(day)
            all_mins = sorted(glob(os.path.join(path, day, '*')))
            print('all mins ', len(all_mins))

            for minute in all_mins:
                minute_name = os.path.basename(minute)
                imgs = glob(os.path.join(minute, '*.png'))

                for img_file in imgs:
                    day_time = os.path.basename(img_file).split('_')
                    str_day, str_time = day_time[0], day_time[1]

                    im_name = f'{str_day}_{str_time}_{sensor}_{home}.png'     
                    try:
                        im = open_im(img_file)
                        img_list = im.resize((img_sz, img_sz), bil)
                        
                        target_dir = make_storage_directory(os.path.join(write_location, str_day, str_time[0:4]))
                        img_list.save(os.path.join(target_dir, im_name))
                        F += 1

                    except Exception as e:
                        print(f'Pillow error: {e}')

            end = datetime.now()
            print(f'Time to process day {day}: {str(end-start).split(".")[0]}. Number of files: {F}')



if __name__ == '__main__':

    for hub in hubs:
        print(f' hub: {hub}\n stored: {path}\n house: {H_num}\n write: {save_root}\n start: {start_date}\n end: {end_date}')

        I = ImageFile(hub, path, H_num, save_root, start_date, end_date, img_name, home_system)
        I.main()
