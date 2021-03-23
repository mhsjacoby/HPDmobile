import os
import sys
import csv
import ast
import json
from datetime import datetime
import numpy as np
import pandas as pd
from collections import defaultdict



class AudioChecker():
    def __init__(self, server_id, days_to_check, test, display_output = True, write_file = True):
        self.server_id = server_id
        self.days_to_check = days_to_check
        self.test = test
        self.display_output = display_output 
        self.write_file = write_file        

        self.import_conf(self.conf())
        self.root = self.conf_dict['img_audio_root']
        self.root_dir = os.path.join(self.root, self.server_id, 'audio')
        self.store = self.conf_dict['store_location']

        self.audio_tape_length = str(self.conf_dict['audio_tape_length'])
        self.correct_files_per_dir = int(60/int(self.audio_tape_length))
        self.end_sec = str(60-int(self.audio_tape_length)) 

        self.date_folders = self.get_date_folders(self.root_dir)
        self.date_dirs = [str(day.date()) for day in pd.date_range(start = self.day1, end = self.dayn, freq = 'D').tolist()]
        self.missing_days = [day for day in self.date_dirs if day not in self.date_folders]   
        self.pi_files_dir = os.path.join(self.root, self.server_id, 'audio_from_pi')
        #self.store_dir = os.path.join(self.store, self.server_id + '_audio_output_dicts')  
        self.write_name = self.server_id + '_audio_' 
        self.store_dir = os.path.join(self.store, str(datetime.now().date()) + '_output', 'audio')  

        self.day_summary = {}
        self.day_full = {}
        self.first_last = {}
        self.pi_dict = {}
        self.found_on_pi = []
        self.output_exists = False

  
    def conf(self):
        if self.test:
            return '/Users/maggie/Desktop/HPD_test_data/test-H1/client_conf_test.json'
        else:
            return '/root/client/client_conf.json'


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
                   
            
    def get_all_mins(self, day, hr_mins):
        date_path = os.path.join(self.root_dir, day)
        hr_mins.sort()
        min_i, min_f = hr_mins[0], hr_mins[-1]
        self.first_last = min_i, min_f
        b_f = str(day + ' 00:00:00')
        e_f = str(day + ' 23:59:' + self.end_sec)     
        b_dt = datetime.strptime((day + ' ' + min_i), '%Y-%m-%d %H%M')
        e_dt = datetime.strptime((day + ' ' + min_f + self.end_sec), '%Y-%m-%d %H%M%S')      
        self.expected_wavs = pd.date_range(b_dt, e_dt, freq = self.audio_tape_length + 'S').tolist()
        self.all_seconds = pd.date_range(b_f, e_f, freq = self.audio_tape_length + 'S').tolist()
        self.expected_dirs = pd.date_range(b_dt, e_dt, freq = '60S').tolist()
        #self.all_minutes = pd.date_range(b_f, e_f, freq = '60S').tolist()
        

    def finder(self):
        for wav in self.wavs:
            dt = datetime.strptime(wav.split('_')[0], '%Y-%m-%d %H%M%S')
            try:
                ind = self.expected_wavs.index(dt)
                self.expected_wavs.pop(ind)
            except:
                self.duplicates += 1
                self.duplicates_ts.append(dt.strftime('%Y-%m-%d %H:%M:%S'))
                pass

    def check_pi(self, d):
        self.found_on_pi = []
        self.pi_dict = defaultdict(list)
        self.pi_wavs = []
        pi_hrs = self.mylistdir(os.path.join(self.pi_files_dir, d))
        for hr_min in pi_hrs:
            temp = os.path.join(self.pi_files_dir, d, hr_min)
            if os.path.isdir(temp):
                pi_hr_wavs = self.mylistdir(os.path.join(self.pi_files_dir, d, hr_min))
                pi_hr_wavs = [x for x in pi_hr_wavs if x.endswith('.wav')]
                pi_hr_wavs = [datetime.strptime(x.split('_')[0], '%Y-%m-%d %H%M%S') for x in pi_hr_wavs]
                self.pi_wavs.extend(pi_hr_wavs)
        for wav in self.expected_wavs:
            if wav in self.pi_wavs:                   
                ind = self.expected_wavs.index(wav)
                self.expected_wavs.pop(ind)
                self.found_on_pi.append(wav)
        for dt in self.found_on_pi:
            hr = datetime.strftime(dt, '%H%M')
            self.pi_dict[hr].append(datetime.strftime(dt, '%Y-%m-%d %H%M%S'))

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

    def configure_output(self,d):
        if self.write_file or self.display_output:
            missed_seconds = []

            for ts in self.expected_wavs:
                missed_seconds.append(ts.strftime('%Y-%m-%d %H:%M:%S'))
            number_missing = len(self.expected_wavs)
            
            unique_wavs = self.total_wavs - self.duplicates
            perc = unique_wavs / self.expect_num_wavs
            perc_cap = (self.expect_num_wavs - number_missing)/self.expect_num_wavs
            day_perc = unique_wavs / len(self.all_seconds)
            day_perc_pi = (self.expect_num_wavs - number_missing) / len(self.all_seconds)

            self.day_cap_pi = float("{0:.2f}".format(day_perc_pi))
            self.perc_cap = float("{0:.2f}".format(perc))
            self.perc_cap_pi = float("{0:.2f}".format(perc_cap))
            self.day_cap = float("{0:.2f}".format(day_perc))
            self.zero_hours = [hr for hr in self.zero_dirs if self.zero_dirs[hr] == 60]
                            
            output_dict_write = {
                'Start Time': datetime.strptime(self.first_last[0], '%H%M').strftime('%H:%M'),
                'End Time': datetime.strptime(self.first_last[1], '%H%M').strftime('%H:%M'),
                'Expected number of wavs': self.expect_num_wavs,
                'Number of unique wavs': unique_wavs,
                'Total number of duplicates': self.duplicates,
                'Number of not captured wavs': len(self.expected_wavs),
                'Percent of wavs captured': self.perc_cap,
                'Percent of the day captured': self.day_cap,
                'Expected number of directories': len(self.expected_dirs),
                'Number of directories w/ correct number wavs': len(self.count_correct),
                'Number of directories w/ incorrect number wavs': len(self.count_other),
                'Number of directories w/ zero wavs': len(self.num_zero_dirs),
                'Directories per hour w/ zero wavs': self.zero_dirs,
                'Hours with no wavs': self.zero_hours
                #'Percent captured including pi': self.perc_cap_pi,
                #'Percent of the day captured including pi': self.day_cap_pi,                
                #'Number of files found on pi': len(self.found_on_pi),
                #'Files found on pi': self.pi_dict
            }
            
            output_dict_display = {
                'Start Time': datetime.strptime(self.first_last[0], '%H%M').strftime('%H:%M'),
                'End Time': datetime.strptime(self.first_last[1], '%H%M').strftime('%H:%M'),
                'Expected number of wavs': self.expect_num_wavs,
                'Number not captured': len(self.expected_wavs),
                'Percent of wavs captured': self.perc_cap,
                'Directories per hour w/ zero wavs': self.zero_dirs,
                'Hours with no wavs': self.zero_hours
                #'Percent captured including pi': self.perc_cap_pi,
                #'Percent of the day captured': self.day_cap,
                #'Percent of the day captured including pi': self.day_cap_pi,  
                #'Number of files found on pi': len(self.found_on_pi)
            }            
                        
            return output_dict_write, output_dict_display
   
    
    def main(self):
        days_n = int(self.days_to_check)
        if days_n > len(self.date_folders):
            print("Not enough days exist. Please try a smaller number.")
            return(False)
        for d in self.date_folders[-days_n:]:
            hr_min_dirs = self.mylistdir(os.path.join(self.root_dir, d))
            self.get_all_mins(d, hr_min_dirs)
            self.expect_num_wavs = len(self.expected_wavs)
            self.total_wavs = 0  
                       
            self.wavs = []
            self.count_correct = {}
            self.zero_dirs = {}
            self.count_other = {}
            self.num_zero_dirs = []
            self.zero_hours = []
            self.duplicates = 0
            self.duplicates_ts = []         
            
            for hr_min in hr_min_dirs:
                temp = os.path.join(self.root_dir, d, hr_min)
                if os.path.isdir(temp):
                    self.wavs = self.mylistdir(os.path.join(self.root_dir, d, hr_min))
                    self.wavs = [x for x in self.wavs if x.endswith('.wav')]
                    self.finder()
                    self.total_wavs += len(self.wavs)
                    
                    hr = datetime.strptime(hr_min,'%H%M').strftime('%H:00')
                    if len(self.wavs) == self.correct_files_per_dir:
                        self.count_correct[hr_min] = self.correct_files_per_dir
                    elif len(self.wavs) == 0:
                        self.num_zero_dirs.append(hr_min)
                        if hr not in self.zero_dirs:
                            self.zero_dirs[hr] = 1
                        else:
                            self.zero_dirs[hr] += 1
                    else:
                        self.count_other[hr_min] = len(self.wavs)

            # self.pi_files = os.path.join(self.pi_files_dir, d)
            # if len(self.expected_wavs) > 0 and os.path.exists(self.pi_files):
            #     self.check_pi(d)
                
            output_dict = self.configure_output(d)           
            if not self.output_exists: 
                print('Date: {}, Sensor: {}'.format(d, self.server_id))
                self.displayer(output_dict[1])
            self.writer(output_dict[0], d) 
            self.day_summary[d] = output_dict[1]
            #self.day_full[d] = output_dict[0]

        self.writer(self.day_summary, 'all_days')
        


if __name__ == '__main__':
    server_id = sys.argv[1]
    days = sys.argv[2]

    if len(sys.argv) > 3:
        test = sys.argv[3]
    else:
        test = False

    a = AudioChecker(server_id, days, test)
    a.main()