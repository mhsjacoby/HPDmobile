# Updated 9/15/2019 - 

import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime
from PIL import Image
import pickle
import gzip
import json
import collections

"""
This class takes the raw images that are saved on a server (antsle)
or in similar folder structure on a computer, and turns the images 
into arrays, reduces the size (from 336 x 336 to 112 x 112) and
pickles and compresses the result by hour. 

This file is meant to be used in conjunction with 'img_extract.py"
"""


NewImage = collections.namedtuple('NewImage', 'day time data')



class DataFile():
    def __init__(self, on_line, sensor, files_dir, house, write_loc):
        self.on_line = on_line
        self.sensor = sensor
        self.path = files_dir   
        # self.dark_days = {}
        # self.dark_days_summary = {}
        self.home = house
        self.write_path = write_loc
        self.get_params()  


    def get_params(self, filetype):
        today = datetime.now().strftime('_%Y-%m-%d')
        self.write_location = os.path.join(self.write_path, self.home + file_type + self.sensor + today)
        print(self.write_location)
        try:
            if not os.path.isdir(self.write_location):
                print('Making directory: {}'.format(self.write_location))
                os.makedirs(self.write_location)
        except Exception as e:
            print('Error making directory {}: {}'.format(self.write_location, e))

    def mylistdir(self, directory):
        filelist = os.listdir(directory)
        return [x for x in filelist if not (x.startswith('.') or 'Icon' in x)]

    def get_time(self, file_name):
        day_time = datetime.strptime(file_name.strip('_photo.png'), '%Y-%m-%d %H%M%S')
        return day_time.strftime('%Y-%m-%d %H%M%S')

    # def load_image(self, png):
    #     im = Image.open(png)
    #     im_array = np.array(list(im.getdata()))
    #     small_img = im.resize((112,112), Image.BILINEAR)
    #     ave_pxl = np.mean(im_array)
    #     return small_img if ave_pxl > 10 else 0

    """
    The following method creates a pandas dataframe for all images that 
    are supposed to be present. It is not active now
    """

    def pickle_object(self, entry, fname, day_loc):
        print('time is: {}'.format(datetime.now().strftime('%H:%M:%S')))
        if not os.path.isdir(day_loc):
            os.makedirs(day_loc)
            print('Making day: {}'.format(day_loc))
        f = gzip.open(os.path.join(day_loc,fname), 'wb')
        pickle.dump(entry, f)
        f.close() 
        print('File written: {}'.format(fname))

    def write_json(self, output_dict, day):
        json_files_stored = os.path.join(self.write_location, 'black_image_dicts')
        if not os.path.isdir(json_files_stored):
            os.makedirs(json_files_stored)
        fname = day + '_dark_images.json'
        write_file = os.path.join(json_files_stored, fname)
        if not os.path.exists(write_file):
            print('Writing dark images for day {} to file {}'.format(day, write_file))
            with open(write_file, 'w+') as f:
                f.write(json.dumps(output_dict))
        else:
            print('{} already exists.'.format(write_file))


    def main(self):
        for day in sorted(self.mylistdir(self.path)):
            print(day)
            dark_hrs = []
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
                            try:
                                img_list = self.load_image(os.path.join(self.path, day, minute, img_file))
                                if img_list == 0:
                                    dark_mins.append(str_time)
                                else:
                                    str_time = NewImage(day=str_day, time=str_time, data=img_list)
                                    hr_entry.append(str_time)

                            except Exception as e:
                                print('Pillow error: {}'.format(e))
                    if len(dark_mins) > 0:
                        dark_hrs.append((hr, len(dark_mins)))
                        black_images[hr] = dark_mins

                    if len(hr_entry) > 0:    
                        fname = day + '_' + hr + '_' + self.sensor + '_' + self.home + '.pklz'
                        write_day = os.path.join(self.write_location,str_day)

                        try:
                            self.pickle_object(hr_entry, fname, write_day)
                        except Exception as e:
                            print('Pickle error: {}'.format(e))
                    else:
                        print('No images for {} hour: {}'.format(day, hr))
                else:
                    print('No directories for {} hour: {}'.format(day, hr))

            self.dark_days_summary[day] = dark_hrs
            self.write_json(black_images, day)
            print(self.dark_days_summary)
        
            


if __name__ == '__main__':
    on_line = True if len(sys.argv) > 1 else False
    sensor = sys.argv[1] if len(sys.argv) > 1 else 'BS1'
    stored_loc = sys.argv[2] if len(sys.argv) > 1 else '/Users/maggie/Desktop/HPD_mobile_data/HPD_mobile-H1/BS1/img'
    house = sys.argv[3] if len(sys.argv) > 1 else 'H1'
    write_loc = sys.argv[4] if len(sys.argv) > 1 else '/Users/maggie/Desktop/HPD_mobile_data/HPD_mobile-H1/'
    I = ImageFile(on_line, sensor, stored_loc, house, write_loc)
    I.main()
