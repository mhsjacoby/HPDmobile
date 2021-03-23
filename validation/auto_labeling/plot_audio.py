"""
plot_audio.py

"""

import os
import csv
import sys
from glob import glob
import numpy as np
import pandas as pd
from datetime import datetime
import argparse
import matplotlib.pyplot as plt


import scipy.io.wavfile
# from scipy.fftpack import dct
# from sklearn.preprocessing import scale

import warnings
warnings.filterwarnings("ignore")

# from AudioFunctions import *
# from gen_argparse import *
from my_functions import *

ybounds = (-20000000,20000000)

def plot_wavs(wav, fname, fs=80000):

    x = np.linspace(0, len(wav) / fs, num=len(wav))
    
    plt.figure(1)
    plt.ticklabel_format(style='plain')
    plt.plot(x, wav)
    plt.xlabel('Time (seconds)')
    plt.ylabel('Signal Amplitude')
    plt.ylim(ybounds)
    plt.tight_layout()
    plt.savefig(os.path.join(save_loc, f'{fname}.png'))

    plt.clf()




if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Plotting audio waveforms to determine noise levels.")

    parser.add_argument('-path', '--path', type=str, help='path of stored data')
    # parser.add_argument('-save_location', '--save', default='', type=str, help='location to store files (if different from path')

    args = parser.parse_args()

    path = args.path
    # save_loc = args.save_location
    save_loc = make_storage_directory(os.path.join(path, 'plots'))

    wav_files = sorted(glob(os.path.join(path, '*.wav')))

    for wav_path in wav_files:
        try:
            _, wav = scipy.io.wavfile.read(wav_path)
            signal = wav - np.mean(wav)
            fname = os.path.basename(wav_path).strip('.wav')
            plot_wavs(signal, fname)

        except Exception as e:
            print(f'Error processing file {wav_path}: {e}')




    




