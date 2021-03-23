import os
import sys
import csv
import ast
import json
from datetime import datetime
import numpy as np
import pandas as pd
from collections import defaultdict



class ImageChecker():
    def __init__(self, home, server_id, days_to_check, data_loc = False, display_output = True, write_file = True):
        self.home = home
        self.server_id = server_id
        self.days_to_check = days_to_check
        self.display_output = display_output 
        self.write_file = write_file  
        self.data_loc = data_loc      
        self.conf()
        self.root_dir = os.path.join(self.root, self.server_id, 'img')

        # self.import_conf(self.conf())
        # self.root = self.conf_dict['img_audio_root']
        # self.store = self.conf_dict['store_location']

        self.correct_files_per_dir = 60
        self.correct_dirs_per_day = 1440
        self.correct_images_per_day = self.correct_files_per_dir * self.correct_dirs_per_day

        self.date_folders = self.get_date_folders(self.root_dir)
        self.date_dirs = [str(day.date()) for day in pd.date_range(start = self.day1, end = self.dayn, freq = 'D').tolist()]
        self.missing_days = [day for day in self.date_dirs if day not in self.date_folders]   
        self.store_dir = os.path.join(self.store, str(datetime.now().date()) + '_output', 'images')  
        self.write_name = self.server_id + '_img_' 

        self.day_summary = {}
        self.day_full = {}
        self.first_last = {}
        self.output_exists = False
        self.images_per_day = {}
        self.summary = {}

    def conf(self):
        if not self.data_loc:
            self.import_conf('/root/client/client_conf.json')
            self.root = self.conf_dict['img_audio_root']
            self.store = self.conf_dict['store_location']
        else:
            self.root = self.data_loc
            self.store = os.path.join(self.root, 'Summaries', 'FileCounts')


    def import_conf(self, path):
        with open(path, 'r') as f:
            self.conf_dict = json.loads(f.read())
        
    def mylistdir(self, directory):
        filelist = os.listdir(directory)
        return [x for x in filelist if not (x.startswith('.') or 'Icon' in x)] 
    
    def get_date_folders(self, path):
        date_folders = self.mylistdir(path)
        date_folders.sort()
        self.day1, self.dayn = date_folders[0], date_folders[-1]
        return date_folders   

    def count_images(self, day):
        total_imgs = 0
        for folder in self.hr_min_dirs:
            #print(folder)
            path = os.path.join(self.root_dir, day, folder)
            img_per_min = len(self.mylistdir(path))
            total_imgs += img_per_min
            if img_per_min == self.correct_files_per_dir:
                self.count_correct.append(folder)
            if img_per_min == 0:
                self.zero_hours.append(folder)
            if img_per_min <= 30:
                self.less_than_30.append(folder)
        return total_imgs

           
 
    def writer(self, output_dict, d):
        self.output_exists = False
        if self.write_file:
            if not os.path.isdir(self.store_dir):
                os.makedirs(self.store_dir)
            b = self.write_name + d + '.json'
            write_file = os.path.join(self.store_dir, b)
            if not os.path.exists(write_file):
                print('Writing file to: {} \n'.format(write_file))
                with open(write_file, 'w+') as f:
                    f.write(json.dumps(output_dict))
            else:
                print('{} already exists \n'.format(write_file))
                self.output_exists = True
    
    def displayer(self, output_dict):
        if self.display_output:
            for key in output_dict:
                print(key, ': ', output_dict[key])
            print('\n')
        else:
            print('No output')

    def write_summary(self, summary_dict):
        fname = os.path.join(self.store, '{}-{}-image-summary.txt'.format(self.home, self.server_id))
        with open(fname, 'w+') as writer:
            for day in summary_dict:
                day_details = summary_dict[day]
                writer.write(day_details + '\n')   
        writer.close()
        print(fname + ': Write Sucessful!')

    def configure_output(self,d):
        if self.write_file or self.display_output:

            perc = self.total_imgs / self.correct_images_per_day
            self.perc_cap = float("{0:.2f}".format(perc))
            non_zero_dirs = [i for i in self.hr_min_dirs if i not in self.zero_hours]
            avg_imgs = self.total_imgs / len(non_zero_dirs)

            print(d)
            print(self.first_last)
            F1, F2 = self.first_last[d][0], self.first_last[d][1]
            s = (f'({F1[0:2]}:{F1[2:4]}, {F2[0:2]}:{F2[2:4]})')
            Summary = '{} {} {} {}'.format(self.server_id, d, s, self.perc_cap)
                            
            output_dict_write = {
                # 'Start Time': datetime.strptime(self.first_last[0], '%H%M').strftime('%H:%M'),
                # 'End Time': datetime.strptime(self.first_last[1], '%H%M').strftime('%H:%M'),
                'Expected number of images': self.correct_images_per_day,
                'Percent of images captured': self.perc_cap,
                'Expected number of directories': self.correct_dirs_per_day,
                'Average number of images per non-zero_folder': avg_imgs,
                'Number of directories w/ correct number images': len(self.count_correct),
                'Number of directories w/ zero images': len(self.zero_hours),
                'Hours with no images': self.zero_hours,
                'Summary': Summary
            }
            
            output_dict_display = {
                # 'Start Time': datetime.strptime(self.first_last[0], '%H%M').strftime('%H:%M'),
                # 'End Time': datetime.strptime(self.first_last[1], '%H%M').strftime('%H:%M'),
                'Expected number of images': self.correct_images_per_day,
                'Percent of images captured': self.perc_cap,
                'Expected number of directories': self.correct_dirs_per_day,
                'Number of directories w/ correct number images': len(self.count_correct),
                'Number of directories w/ zero images': len(self.zero_hours),
                'Average number of images per non-zero_folder': avg_imgs,
                'Hours with no images': self.zero_hours,
                'Summary': Summary
            }            
                        
            return output_dict_write, output_dict_display, Summary
   
    
    def main(self):
        days_n = int(self.days_to_check)
        if days_n > len(self.date_folders):
            print('Not enough days exist. Using {} days'.format(len(self.date_folders)))
            days_n = len(self.date_folders)

        for d in self.date_folders[-days_n:]:
            self.hr_min_dirs = sorted(self.mylistdir(os.path.join(self.root_dir, d)))
            min_1, min_L = self.hr_min_dirs[0], self.hr_min_dirs[-1]
            self.first_last[d] = min_1, min_L
            self.zero_hours = []
            self.less_than_30 = []
            self.count_correct = []
            self.total_mins = len(self.hr_min_dirs)
            self.total_imgs = self.count_images(d)   
                
            output_dict = self.configure_output(d)           
            if not self.output_exists: 
                print('Date: {}, Sensor: {}'.format(d, self.server_id))
                self.displayer(output_dict[1])
            self.writer(output_dict[0], d) 
            self.summary[d] = output_dict[2]

        self.write_summary(self.summary)





if __name__ == '__main__':
    home = sys.argv[1]
    server_id = sys.argv[2]
    days = sys.argv[3]
    data_loc = sys.argv[4] if len(sys.argv) > 4 else False

    a = ImageChecker(home, server_id, days, data_loc)
    a.main()
