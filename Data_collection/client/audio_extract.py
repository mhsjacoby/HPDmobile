# Updated 10/17/2019

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
import csv


NewAudio = collections.namedtuple('NewAudio', 'day time data')



"""
This class takes a list of pickled objects and extracts the audio files to .txt.
The pickled objects are organized by hour.

Run this program by specifying the path to the picked files, and the 
target save directory. 

eg:
python3 ARPA-E-Sensor/client/audio_extract.py /Volumes/SEAGATE-9/h3-black
/RS1/H3-RS1-audio-pkl/ /Users/maggie/Desktop/HPD_mobile_data/HPD_mobile-H3/H3-black/RS1/audio

This file extracts audio that were pickled with 'audio_save.py'

"""





class ImageExtract():
    def __init__(self, root_dir, store_dir):
        self.root_dir = root_dir
        self.store_location = store_dir

    def unpickle(self, pickled_file):
        f = gzip.open(pickled_file, 'rb')
        unpickled_obj = pickle.load(f)
        f.close()
        return unpickled_obj

    def mylistdir(self, directory):
        filelist = os.listdir(directory)
        return [x for x in filelist if x.startswith('2019-')]
    
    def extract_audio(self, audio_data):
        pass



    def main(self):
        pickled_days = sorted(self.mylistdir(self.root_dir))
        for dayF in pickled_days:
            pickled_files = sorted(self.mylistdir(os.path.join(self.root_dir, dayF)))

            for f in pickled_files:
                print('time is: {}'.format(datetime.now().strftime('%H:%M:%S')))
                print('unpickling file: {}'.format(f))
                pickleName = f.strip('_audio.pklz')
                Names = pickleName.split('_')
                day, hour, sensor, home = Names[0], Names[1], Names[2], Names[3]
                if day != dayF:
                    print(f'{pickleName} is in the wrong folder ({dayF})')

                new_store_dir = os.path.join(self.store_location, home, sensor, 'audio', day)
                hour_fdata = self.unpickle(os.path.join(self.root_dir, dayF, f))

                for entry in [x for x in hour_fdata if len(hour_fdata) > 0]:
                        #new_audio = entry.data                    
                        full_audio_dir = os.path.join(new_store_dir, str(entry.time)[0:4])
                        if not os.path.isdir(full_audio_dir):
                            os.makedirs(full_audio_dir)
                        fname = str(entry.day + '_' + entry.time + '_' + sensor + '_' + home + '_audio.csv')
                        new_audio = [[x] for x in entry.data]
                        if not os.path.exists(os.path.join(full_audio_dir, fname)):
                            with open(os.path.join(full_audio_dir, fname), 'w') as csvFile:
                                writer = csv.writer(csvFile)
                                writer.writerows(new_audio)
                            csvFile.close()

                        #     new_audio.save(os.path.join(full_audio_dir, fname))
                        else:
                            print('Audio file exists: {}'.format(os.path.join(full_audio_dir,fname)))


if __name__ == '__main__':
    pickle_location = sys.argv[1]
    new_file_location = 'sys.argv[2]'

    P = ImageExtract(pickle_location, new_file_location)
    P.main()
