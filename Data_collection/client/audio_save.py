# Updated 9/12/2019

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
import scipy.io.wavfile


NewAudio = collections.namedtuple('NewAudio', 'day time data')


class AudioFile():
    def __init__(self, sensor, files_dir, house, write_loc, start_date):
        self.sensor = sensor
        self.path = files_dir   
        self.home = house
        self.write_path = write_loc
        self.start_date = start_date
        self.get_params()  


    def get_params(self):
        #today = datetime.now().strftime('_%Y-%m-%d')
        self.write_location = os.path.join(self.write_path, self.home + '-' + self.sensor + '-audio-pkl')
        print('writing to: {}'.format(self.write_location))
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
        day_time = datetime.strptime(file_name.strip('_audio.wav'), '%Y-%m-%d %H%M%S')
        return day_time.strftime('%Y-%m-%d %H%M%S')

    def read_audio(self, wav_path):
        _, wav = scipy.io.wavfile.read(wav_path)
        return wav

    def pickle_object(self, entry, fname, day_loc):
        print('time is: {}'.format(datetime.now().strftime('%H:%M:%S')))
        if not os.path.isdir(day_loc):
            os.makedirs(day_loc)
            print('Making day: {}'.format(day_loc))
        f = gzip.open(os.path.join(day_loc, fname), 'wb')
        pickle.dump(entry, f)
        f.close() 
        print('File written: {}'.format(fname))
   
    def main(self):
        print('Start date: {}'.format(self.start_date))
        for day in sorted(self.mylistdir(self.path)):
            try:
                if datetime.strptime(day, '%Y-%m-%d') >= datetime.strptime(self.start_date, '%Y-%m-%d'):
                    print(day)
                    hours = [str(x).zfill(2) + '00' for x in range(0,24)]
                    all_mins = sorted(self.mylistdir(os.path.join(self.path, day)))
                    for hr in hours:
                        hr_entry = []
                        this_hr = [x for x in all_mins if x[0:2] == hr[0:2]]
                        if len(this_hr) > 0:
                            for minute in sorted(this_hr):
                                for wav_file in sorted(self.mylistdir(os.path.join(self.path, day, minute))):
                                    day_time = self.get_time(wav_file).split(' ')
                                    str_day, str_time = day_time[0], day_time[1]
                                    try:
                                        audio_list = self.read_audio(os.path.join(self.path, day, minute, wav_file))
                                        str_time = NewAudio(day=str_day, time=str_time, data=audio_list)
                                        hr_entry.append(str_time)
                                        
                                    except Exception as e:
                                        print('Audio error: {}'.format(e))
                            if len(hr_entry) > 0:
                                fname = day + '_' + hr + '_' + self.sensor + '_' + self.home + '_audio.pklz'
                                write_day = os.path.join(self.write_location, str_day)

                                try:
                                    self.pickle_object(hr_entry, fname, write_day)
                                except Exception as e:
                                    print('Pickle error: {}'.format(e))
                            else:
                                print('No audio files for {} hour: {}'.format(day, hr))

                        else:
                            print('No directories for {} hour {}'.format(day, hr))
                else:
                    print('Day {} is before start date of {}'.format(day, self.start_date))
            except Exception as e:
                print('Compare error: {}'.format(e))

                            
if __name__ == '__main__':
    sensor = sys.argv[1]
    stored_loc = sys.argv[2]
    house = sys.argv[3]
    write_loc = sys.argv[4]
    start_date = sys.argv[5] if len(sys.argv) > 5 else '2019-01-01'

    I = AudioFile(sensor, stored_loc, house, write_loc, start_date)
    I.main()