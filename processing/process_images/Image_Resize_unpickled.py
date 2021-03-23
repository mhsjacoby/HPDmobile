"""
Image_Resize_unpickled.py
Maggie Jacoby
created 03/22/2020
"""

import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime
from PIL import Image
import json


"""
This class takes the raw images that are saved on a hard drive 
(as extracted from the antlse) or in similar folder structure on a computer, 
and reduces the size (from 336 x 336 to 112 x 112), removes the dark images, 
and counts imagees

This file is meant to rpelace 'img_save.py' and 'img_extract.py' for already unpickled images
"""



class ImageFile():
    def __init__(self, sensor, files_dir, house, write_loc, start_date):
        self.sensor = sensor
        self.original_loc = files_dir   
        self.dark_days = {}
        self.dark_days_summary = {}
        self.home = house
        self.write_path = write_loc
        self.start_date = start_date
        self.get_params()  
        self.total_per_day = 86400
        self.count_of_dark = {}
        # self.end_date = '2019-03-11'



    def get_params(self):
        #today = datetime.now().strftime('_%Y-%m-%d')
        # self.path = os.path.join(self.original_loc, self.sensor, 'img')
        self.path = os.path.join(self.original_loc, 'img')

        print(f'getting files from: {self.path}')
        self.write_location = os.path.join(self.write_path, self.home, self.sensor, 'img-downsized')
        print(f'resizeing and saving to: {self.write_location}')
        try:
            if not os.path.isdir(self.write_location):
                print(f'Making directory: {self.write_location}')
                os.makedirs(self.write_location)
        except Exception as e:
            print(f'Error making directory {self.write_location}: {e}')


    def mylistdir(self, directory, bit='', end=True):
        filelist = os.listdir(directory)
        if end:
            return [x for x in filelist if x.endswith(f'{bit}') and not x.endswith(f'v2')]
        else:
            return [x for x in filelist if x.startswith(f'{bit}') and not x.endswith(f'v2')]
        


    def get_time(self, file_name):
        day_time = datetime.strptime(file_name.strip('_photo.png'), '%Y-%m-%d %H%M%S')
        return day_time.strftime('%Y-%m-%d %H%M%S')

    def load_image(self, png):
        im = Image.open(png)
        im_array = np.array(list(im.getdata()))
        small_img = im.resize((112,112), Image.BILINEAR)
        ave_pxl = np.mean(im_array)
        return small_img if ave_pxl > 10 else 0


    def count_dark(self, day, day_dark_list):
        day_set = set()
        for d in day_dark_list:        
            day_set = set.union(day_set, day_dark_list[d])
        num_dark = len(list(day_set))
        self.count_of_dark[day] = num_dark


    def write_summary(self, days):
        store_dir = os.path.join(self.write_path, self.home, self.sensor, 'Summaries')
        if not os.path.isdir(store_dir):
            os.makedirs(store_dir)
        fname = os.path.join(store_dir, f'{self.home}-{self.sensor}-img-summary.txt')
        with open(fname, 'w+') as writer:
            writer.write('hub day %Capt %Dark \n')
            for day in days:
                # if self.dark_images_counted:
                try:
                    total_captured = self.count_of_dark[day] + self.Day_Summary[day]
                    try:
                        total_dark = self.count_of_dark[day]/self.total_per_day
                        D_perc = 'f{total_dark:.2}'
                    except Exception as e:
                        print(f'except: {e}')
                        D_perc = 0.00
                except:
                    total_captured = self.Day_Summary[day]
                    D_perc = 0.00
                try:
                    total = total_captured/self.total_per_day
                    T_perc = 'f{total:.2}'
                except Exception as e:
                    print(f'except: {e}')
                    T_perc = 0.00
                details = f'{self.sensor} {day} {T_perc} {D_perc}'
                writer.write(details + '\n')
        writer.close()
        print(f'{fname}: Write Successful!')
                




    def main(self):
        print(f'Start date: {self.start_date}')
        all_days = sorted(self.mylistdir(self.path, '2019-', end=False))
        self.Day_Summary = {d:0 for d in all_days}

        for day in all_days:
            try:
                # if datetime.strptime(day, '%Y-%m-%d') >= datetime.strptime(self.start_date, '%Y-%m-%d') and datetime.strptime(day, '%Y-%m-%d') <= datetime.strptime(self.end_date, '%Y-%m-%d'):
                if datetime.strptime(day, '%Y-%m-%d') >= datetime.strptime(self.start_date, '%Y-%m-%d'):

                    print(day)
                    black_images = {}
                    hours = [str(x).zfill(2) + '00' for x in range(0,24)]
                    all_mins = sorted(self.mylistdir(os.path.join(self.path, day)))

                    for hr in hours:
                        hr_entry = []
                        dark_mins = []
                        this_hr = [x for x in all_mins if x[0:2] == hr[0:2]]
                        if len(this_hr) > 0:
                            for minute in sorted(this_hr):
                                for img_file in sorted(self.mylistdir(os.path.join(self.path, day, minute))):
                                    day_time = self.get_time(img_file).split(' ')
                                    str_day, str_time = day_time[0], day_time[1]
                                    if str_day != day:
                                        print(f'day mismatch! file {img_file} is in day {day}')
                            
                                    im_name = f'{str_day}_{str_time}_{self.sensor}_{self.home}.png'     
                                    try:
                                        img_list = self.load_image(os.path.join(self.path, day, minute, img_file))
                                        if img_list == 0:
                                            dark_mins.append(str_time)
                                        else:
                                            target_dir = os.path.join(self.write_location, str_day, str_time[0:4])
                                            if not os.path.isdir(target_dir):
                                                os.makedirs(target_dir)
                                            if not os.path.exists(os.path.join(target_dir, im_name)):
                                                img_list.save(os.path.join(target_dir, im_name))
                                                hr_entry.append(str_time)
                                                self.Day_Summary[day] += 1 
                                            else:
                                                # print(f'image already exists: {im_name}')
                                                duplicate_img_dir = os.path.join(self.write_location, 'duplicateImages', self.sensor)
                                                if not os.path.isdir(duplicate_img_dir):
                                                    os.makedirs(duplicate_img_dir)
                                                dup_fname = im_name.strip('.png') + '_dup.png'
                                                img_list.save(os.path.join(duplicate_img_dir, dup_fname))    


                                    except Exception as e:
                                        print(f'Pillow error: {e}')
                            if len(dark_mins) > 0:
                                black_images[hr] = dark_mins
                            if len(hr_entry) > 0:
                                print(f'Total entries for {hr} = {len(hr_entry)}')
                            else:
                                print(f'No images for {day} hour: {hr}')
                        else:
                            print(f'No directories for {day} hour: {hr}')

                    try:
                        self.count_dark(day, black_images)
                    except Exception as e:
                        print(f'Error in day {day}: {e}')


                else:
                    print(f'Day {day} is before start date of {self.start_date}')
            except Exception as e:
                print(f'Error: {e}')

        try:
            self.write_summary(all_days)
        except Exception as e:
            print(f'Error writing summary: {e}')

        
            

if __name__ == '__main__':
    stored_loc = sys.argv[1]
    house = stored_loc.strip('/').split('/')[-1]
    write_loc = sys.argv[2]
    start_date = sys.argv[3] if len(sys.argv) > 3 else '2019-01-01'
    sensors = ['RS1']#, 'RS2', 'RS4', 'RS5']

    for sensor in sensors:
        print(f' sensor: {sensor}\n stored: {stored_loc}\n house: {house}\n write: {write_loc}\n start: {start_date}')

        I = ImageFile(sensor, stored_loc, house, write_loc, start_date)
        I.main()
