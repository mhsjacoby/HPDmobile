
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Electrisense Test
# Generated: Fri Feb 15 15:30:49 2019
##################################################

from gnuradio import analog
from gnuradio import blocks
from gnuradio import gr
from gnuradio import uhd
from gnuradio.fft import logpwrfft
from gnuradio.filter import firdes
from optparse import OptionParser

import time
import sys
import os
import numpy as np
from datetime import datetime
from datetime import timedelta
from scipy.signal import medfilt

class data_logger(gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self)

        ############# Define variables #############
        self.samp_rate = 2e6
        self.fc = 100e3
        self.fft_size = 2048
        self.num_avg_window = 25
        self.fileNum = 1
        self.filt_win_size = 501
        self.store_loc = '/root/USRP/'

        self.uhd_usrp_source = uhd.usrp_source(
            ",".join(('addr=192.168.10.2', "")),
            uhd.stream_args(
                cpu_format="fc32",
                channels=range(1),
            ),
        )

        self.uhd_usrp_source.set_samp_rate(self.samp_rate)
        self.uhd_usrp_source.set_center_freq(self.fc, 0)
        self.uhd_usrp_source.set_gain(0,0)
        self.uhd_usrp_source.set_antenna('TX/RX', 0)
        self.uhd_usrp_source.set_bandwidth(1e6, 0)

        self.lpwrfft = logpwrfft.logpwrfft_c(
            sample_rate=self.samp_rate,
            fft_size=self.fft_size,
            ref_scale=2,
            frame_rate=1000,
            avg_alpha=1.0,
            average=False,
        )

        self.data_sink = blocks.vector_sink_f(2048, int(2e6))
        ############# Connect blocks #############
        self.connect((self.uhd_usrp_source,0), (self.lpwrfft, 0))
        self.connect((self.lpwrfft,0), (self.data_sink, 0))
        

    def start_new_file(self):
        self.now = datetime.now()
        print('Time is: {}'.format(self.now.time().strftime('%H:%M:%S')))

        time.sleep(60)
        tb.stop()
        tb.wait()
        n2 = datetime.now()
        self.elapsed_time = n2-self.now

        self.disconnect((self.lpwrfft,0), (self.data_sink, 0))
        self.disconnect((self.uhd_usrp_source,0), (self.lpwrfft, 0))

        processed_data, TIME = self.process_data(self.data_sink.data(), self.fft_size, self.num_avg_window, self.filt_win_size)

        write_loc = os.path.join(self.store_loc, str(self.now.date()), str(self.now.time().strftime('%H00')))
        if not os.path.isdir(write_loc):
            os.makedirs(write_loc)
            print('Making folder: {}'.format(write_loc))
        else:
            print('Folder exists: {}'.format(write_loc))
        #self.filename_filtered = os.path.join(write_loc, str(now.date()) + str(now.time().strftime('_%H%M%S')) + '_filtered.txt')
        self.filename = os.path.join(write_loc, str(self.now.date()) + str(self.now.time().strftime('_%H%M%S')) + '.txt')

        print("New file: " + self.filename)
        
        print('Saving data...')
        # np.savetxt(self.filename_filtered, processed_data_filtered)
        to_save = tuple(zip(TIME, processed_data))
        np.savetxt(self.filename, to_save, fmt='%s')

        print('Complete.')

        self.data_sink = blocks.vector_sink_f(2048, int(2e6))
        self.connect((self.lpwrfft,0),(self.data_sink,0))
        self.connect((self.uhd_usrp_source,0), (self.lpwrfft, 0))
        tb.start()
        print('Collecting Data...')




    def process_data(self, data, fft_size, num_avg_window, filt_win_size):
        print("Processing Data...")
        fs = self.samp_rate

        # Reshape Data
        x = len(data)
        # print('len of data(1): {}'.format(len(data)))
        T = int(len(data)/fft_size)
        data = np.reshape(data, (fft_size, T), order="F")
        # print('len of len of data(2): {}'.format(len(data[0])))
        # print('len of data(2): {}'.format(len(data)))
        # print('len of len of data(2): {}'.format(len(data[0])))
        # print('T: {}'.format(T))

        # Compute Averaged Frames
        spectra_avg = np.zeros((fft_size, int(np.floor(T)/num_avg_window)))
        count = 0
        # print('spectra avg rows {}, cols {}'.format(len(spectra_avg), len(spectra_avg[0])))

        for i in range(0, T-num_avg_window, num_avg_window):
            spectra_avg[:,count] = np.mean(data[:,i:i+num_avg_window-1], axis=1)
            count += 1

        # Abs & Sum each FFT Bin
        [rows, columns] = np.shape(spectra_avg)
        signal = np.zeros(columns)

        # print('rows: {}. columns: {}'.format(rows, columns))

        for i in range(columns):
            signal[i] = np.sum(np.abs(spectra_avg[:,i]))

        ind = np.arange(0, len(signal), 1)
        td_times = [self.now + (i*self.elapsed_time/len(signal)) for i in ind]
        time_ind = [x.strftime('%Y-%m-%d_%H:%M:%S:%f') for x in td_times]

        # print('length of time: {}, length of signal: {}'.format(len(time_ind), len(signal)))
        # print('first, last timepoints: {} and {}'.format(time_ind[0], time_ind[-1]))

        # Normalize and Filter
        # sig_norm = (signal - np.min(signal))/(np.max(signal)-np.min(signal))
        # sig_filt = medfilt(sig_norm, filt_win_size)

        print("Processing Complete.")
        #print('Signal length: {}. Sig_filt length: {}'.format(len(signal), len(sig_filt)))
        return signal, time_ind

def main():
    global tb
    tb = data_logger()
    tb.start()
    print('Starting Data Collection...')


    while 1:
        #c = raw_input("'q' to quite\n")
    
        tb.start_new_file()

        


if __name__ == '__main__':
    main()
