# Updated 03/07/2020 - check titles and count images and black images

import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime
from PIL import Image
import pickle
import gzip
import collections
import json
import cProfile
import re
import itertools

NewImage = collections.namedtuple('NewImage', 'day time data')


"""
This class takes a list of pickled objects and extracts the raw images.
The pickled objects are organized by hour.

Run this program by specifying the path to the picked files, and the 
target save directory. 

eg:
python3 ARPA-E-Sensor/client/img_extract.py /Volumes/SEAGATE-9/h3-black
/RS1/H3-RS1-img-pkl/ /Users/maggie/Desktop/HPD_mobile_data/HPD_mobile-H3/H3-black/

/Volumes/SEAGATE-9/h3-black/RS1/H3-RS1-img-pkl/

This file extracts images that were pickled with 'img_save.py'
"""

class ImageExtract():
    def __init__(self, h_dir, store_loc, sensor, dark_img = True):
        self.sensor_dir = os.path.join(h_dir, sensor)
        self.store_location = store_loc
        self.sensor = sensor
        self.dark_images_counted = dark_img
        self.total_per_day = 86400
        self.count_of_dark = {}
        self.root_dir = self.get_root_dir()
    #     self.get_name()
    #     self.get_home()


    # def get_name(self):
    #     if self.root_dir.endswith('/'):
    #         # self.sensor = self.root_dir.split('/')[-3]
    #         sp_name = self.root_dir.split('/')[-2].split('-')[1]
    #     else:
    #         # self.sensor = self.root_dir.split('/')[-2]
    #         sp_name = self.root_dir.split('/')[-1].split('-')[1]
    #     print(f'Sensor hub: {self.sensor}')
    #     if self.sensor != sp_name:
    #         print(f'Naming convention mismatch! Hub folder: {self.sensor}. Pickle folder: {sp_name}')

    # def get_home(self):
    #     if self.root_dir.endswith('/'):
    #         self.home = self.root_dir.split('/')[-4].split('-')[0]
    #         hp_name = self.root_dir.split('/')[-2].split('-')[0]
    #     else:
    #         self.home = self.root_dir.split('/')[-3].split('-')[0]
    #         hp_name = self.root_dir.split('/')[-1].split('-')[0]
    #     print(f'Home: {self.home}')
    #     if self.home != hp_name:
    #         print(f'Naming convention mismatch! Hub folder: {self.home}. Pickle folder: {hp_name}')        

    def get_root_dir(self):
        flist = os.listdir(self.sensor_dir)
        img_pickles = [x for x in flist if x.endswith('-img-pkl')]
        if len(img_pickles) == 0:
            print(f'No pickles :(')
            sys.exit()
        elif len(img_pickles) > 1:
            print(f'Multiple pickled image folders: {img_pickles}')
        self.home = img_pickles[0].split('-')[0]
        return os.path.join(self.sensor_dir, img_pickles[0])
        


    def unpickle(self, pickled_file):
        try:
            f = gzip.open(pickled_file, 'rb')
            unpickled_obj = pickle.load(f)
            f.close()
            return unpickled_obj
        except Exception as e:
            print(f'Error unpickling file: {di}. Error: {e}')
            return None


    def mylistdir(self, directory):
        filelist = os.listdir(directory)
        return [x for x in filelist if x.startswith('2019-')]

    def extract_images(self, img_data):
        im_data = np.asarray(img_data)
        new_im = Image.new('L', (112, 112))
        flat_data = list(itertools.chain(*im_data))
        new_im.putdata(flat_data)
        return new_im


    def read_dark(self, day):
        di = os.path.join(self.root_dir, 'black_image_dicts', f'{day}_dark_images.json')
        try:
            with open(di, 'r') as f:
                try:
                    day_dark_list = json.loads(f.read())
                except Exception as e:
                    print(f'Error reading dict: {e}')
            day_set = set()
            for d in day_dark_list:
                day_set = set.union(day_set, day_dark_list[d])
            num_dark = len(list(day_set))
            self.count_of_dark[day] = num_dark   
        except Exception as e:
            print(f'Error opening file: {di}. Error: {e}')
     



    def write_summary(self, days):
        store_dir = os.path.join(self.store_location, 'Summaries')
        if not os.path.isdir(store_dir):
            os.makedirs(store_dir)
        fname = os.path.join(store_dir, f'{self.home}-{self.sensor}-img-summary.txt')
        with open(fname, 'w+') as writer:
            writer.write('hub day %Capt %Dark \n')
            for day in days:
                if self.dark_images_counted:
                    try:
                        total_captured = self.count_of_dark[day] + self.Day_Summary[day]
                        total_dark = self.count_of_dark[day]/self.total_per_day
                        D_perc = '{:.2f}'.format(total_dark)
                    except Exception as e:
                        print('except: {}'.format(e))
                        D_perc = 0.00
                else:
                    total_captured = self.Day_Summary[day]
                    D_perc = 0.00
                try:
                    total = total_captured/self.total_per_day
                    T_perc = '{:.2f}'.format(total)
                except Exception as e:
                    print('except: {}'.format(e))
                    T_perc = 0.00
                details = f'{self.sensor} {day} {T_perc} {D_perc}'
                writer.write(details + '\n')
        writer.close()
        print(f'{fname}: Write Successful!')
                

                


    def main(self):

        print(f'\nStarting to unpickle from {self.root_dir} to {self.store_location} Day is: {datetime.now().strftime("%Y-%m-%d")}')
        pickled_days = sorted(self.mylistdir(self.root_dir))
        self.Day_Summary = {d:0 for d in pickled_days}

        for dayF in pickled_days:
            pickled_files = sorted(self.mylistdir(os.path.join(self.root_dir, dayF)))
            if self.dark_images_counted:
                self.read_dark(dayF)

            for f in pickled_files:
                print(f'time is: {datetime.now().strftime("%H:%M:%S")}')
                print(f'unpickling file: {f}')
                pickleName = f.strip('.pklz')
                Names = pickleName.split('_')
                fday, fhour, fsensor, fhome = Names[0], Names[1], Names[2], Names[3]
                if fsensor != self.sensor:
                    print(f'Hub mismatch!  Hub folder: {self.sensor}. Pickle file: {fsensor}')
                if fhome != self.home:
                    print(f'Home mismatch!  Home folder: {self.home}. Pickle file: {fhome}')

                try:
                    hour_fdata = self.unpickle(os.path.join(self.root_dir, dayF, f))


                    for entry in [x for x in hour_fdata if len(hour_fdata) > 0]:
                        if entry.data != 0:
                            if entry.day != fday:
                                print(f'Mispickled file: {entry.day, entry.time} is in folder: {pickleName}')
                            new_store_dir = os.path.join(self.store_location, self.sensor, 'img-unpickled', entry.day)
                            new_image = self.extract_images(entry.data)
                            full_img_dir = os.path.join(new_store_dir, str(entry.time)[0:4])
                            if not os.path.isdir(full_img_dir):
                                os.makedirs(full_img_dir)

                            fname = str(entry.day + '_' + entry.time + '_' + self.sensor + '_' + self.home + '.png')
                            if not os.path.exists(os.path.join(full_img_dir, fname)):
                                new_image.save(os.path.join(full_img_dir, fname))
                                self.Day_Summary[entry.day] += 1
                            else:
                                print('Image already exists: {}'.format(fname))
                                duplicate_img_dir = os.path.join(self.store_location, 'duplicateImages', self.sensor)
                                if not os.path.isdir(duplicate_img_dir):
                                    os.makedirs(duplicate_img_dir)
                                dup_fname = fname.strip('.png') + '_dup.png'
                                new_image.save(os.path.join(duplicate_img_dir, dup_fname))
                except Exception as e:
                    print('except: {}'.format(e))                
                    
        self.write_summary(pickled_days)



if __name__ == '__main__':
    pickle_location = sys.argv[1] #if len(sys.argv) > 1 else '/Users/maggie/Desktop/HPD_mobile_data/HPD_mobile-H1/pickled_images'
    new_image_location = sys.argv[2] # '/Users/maggie/Desktop/Unpickled_Images'
    # sensors = ['RS1', 'RS2', 'RS3', 'RS4', 'RS5']
    sensors = ['BS5']

    for sensor in sensors:
        print(sensor)
        P = ImageExtract(pickle_location, new_image_location, sensor)
        P.main()


    
    