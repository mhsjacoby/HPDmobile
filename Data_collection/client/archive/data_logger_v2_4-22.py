#!/usr/bin/env python2
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
from datetime import datetime

class data_logger(gr.top_block):
        def __init__(self):
                gr.top_block.__init__(self)

                ############# Define variables #############
                self.samp_rate = 1e6
                self.fc = 45e3

                # now = datetime.now()
                # self.nowtime = now.strftime('%Y-%m-%d-%H%M%S')

                # self.rootdir = "/mnt/disk2/usrp"
                # self.name = self.nowtime + "_first_file.bin"
                # self.filename = os.path.join(self.rootdir, self.name)

                # self.fileNum = 1
                # self.filename = "/home/zerina/data_logging" + str(self.fileNum) + ".bin"

                # self.exists = os.path.isfile(self.filename)

                # while self.exists:
                #         #self.fileNum += 1

                #         #self.filename = "/home/zerina/data_logging" + str(self.fileNum) + ".bin"
                #         now = datetime.now()
                #         self.nowtime = now.strftime('%Y-%m-%d-%H%M%S')

                #         self.rootdir = "/mnt/disk2/usrp"
                #         self.name = self.nowtime + "_first_file.bin"
                #         self.filename = os.path.join(self.rootdir, self.name)


                #         #self.filename = "/home/zerina/data_logging" + str(self.fileNum) + ".bin"
                #         self.exists = os.path.isfile(self.filename)
                # else:
                #         print("New file: " + self.filename)


                ############# Initalize blocks #############
                self.uhd_usrp_source = uhd.usrp_source(
                        ",".join(('addr=192.168.10.2',"")),
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
                        fft_size=2048,
                        ref_scale=2,
                        frame_rate=30,
                        avg_alpha=1.0,
                        average=False,
                )

                self.file_sink = blocks.file_sink(gr.sizeof_float*2048, self.filename, False)
                self.file_sink.set_unbuffered(False)

                ############# Connect blocks #############
                self.connect((self.lpwrfft,0),(self.file_sink,0))
                self.connect((self.uhd_usrp_source,0), (self.lpwrfft, 0))


        # def make_storage_directory(self, root, day, hour):
        #         target_dir = os.path.join(root, day, hour)
        #         if os.path.exists(target_dir):
        #                 return target_dir
        #         else:
        #                 os.makedirs(target_dir)
        #                 return target_dir



        # def start_new_file(self):
        #         time.sleep(30)
        #         tb.stop()
        #         tb.wait()

                self.disconnect((self.lpwrfft,0),(self.file_sink,0))
                self.disconnect((self.uhd_usrp_source,0), (self.lpwrfft, 0))

                print("Starting file...")
                #self.filename = "/home/zerina/data_logging" + str(self.fileNum) + ".bin"
                # now = datetime.now()
                # now_day = now.strftime('%Y-%m-%d')
                # now_hour = now.strftime('%H00')
                # now_time = now.strftime('%H%M%S')
                # self.filename = now_time + '_usrp.bin'
                # self.dir = self.make_storage_directory(self.rootdir, now_day, now_hour) 
                # self.savefile = os.path.join(self.dir, self.filename)
                
                # self.exists = os.path.isfile(self.savefile)
                # while self.exists:
                #         #self.fileNum += 1
                #         #self.filename = "/home/zerina/data_logging" + str(self.fileNum) + ".bin"
                #         now_day = now.strftime('%Y-%m-%d')
                #         now_hour = now.strftime('%H00')
                #         now_time = now.strftime('%H%M%S')
                #         self.filename = now_time + '_usrp.bin'
                #         self.dir = self.make_storage_directory(self.rootdir, now_day, now_hour) 
                #         self.savefile = os.path.join(self.dir, self.filename)
                                
                        
                #         #self.exists = os.path.isfile(self.filename)
                #         self.exists = os.path.isfile(self.savefile)
                self.file_name = '/mnt/disk2/usrp/tests/test_file.bin'
                print("New file: " + self.filename)
                #self.disconnect((self.analog_sig_source,0),(self.file_sink,0))
                self.file_sink = blocks.file_sink(gr.sizeof_float*2048, self.savefile, False)
                self.file_sink.set_unbuffered(False)
                self.connect((self.lpwrfft,0),(self.file_sink,0))
                self.connect((self.uhd_usrp_source,0), (self.lpwrfft, 0))
                tb.start()
                # time.sleep(30)
def main():
        global tb
        tb = data_logger()
        tb.start()

        while 1:
                #c = raw_input("'q' to quite\n")
                tb.start_new_file()
                


if __name__ == '__main__':
        main()



