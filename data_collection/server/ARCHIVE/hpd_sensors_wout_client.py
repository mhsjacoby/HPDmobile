import smbus2 as smbus
import board
import busio
import adafruit_sgp30
import VL53L1X
import Adafruit_DHT
import threading
from datetime import datetime
import time
import pyaudio
import wave
import numpy as np
import wave
import os
import sys
import logging
import subprocess
import json

# logging.basicConfig(filename = '/home/pi/sensors_logfile.log', level = logging.INFO,
#                     format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
#                     datefmt='%d-%m-%Y:%H:%M:%S',)

class HPD_APDS9301():
    def __init__(self):
        # Module variables
        self.i2c_ch = 1
        self.bus = smbus.SMBus(self.i2c_ch)

        # APDS-9301 address on the I2C bus
        self.apds9301_addr = 0x39

        # Register addresses
        self.apds9301_control_reg = 0x80
        self.apds9301_timing_reg = 0x81
        self.apds9301_data0low_reg = 0x8C
        self.apds9301_data1low_reg = 0x8E

        # Read the CONTROL register (1 byte)
        val = self.bus.read_i2c_block_data(self.apds9301_addr, self.apds9301_control_reg, 1)
        
        # Set POWER to on in the CONTROL register
        val[0] = val[0] & 0b11111100
        val[0] = val[0] | 0b11

        # Enable the APDS-9301 by writing back to CONTROL register
        self.bus.write_i2c_block_data(self.apds9301_addr, self.apds9301_control_reg, val)

    # Read light data from sensor and calculate lux
    def read(self):

        # Read channel 0 light value and combine 2 bytes into 1 number
        val = self.bus.read_i2c_block_data(self.apds9301_addr, self.apds9301_data0low_reg, 2)
        ch0 = (val[1] << 8) | val[0]

        # Read channel 1 light value and combine 2 bytes into 1 number
        val = self.bus.read_i2c_block_data(self.apds9301_addr, self.apds9301_data1low_reg, 2)
        ch1 = (val[1] << 8) | val[0]

        # Make sure we don't divide by 0
        if ch0 == 0.0:
            return 0.0

        # Calculate ratio of ch1 and ch0
        ratio = ch1 / ch0

        # Assume we are using the default 13.7 ms integration time on the sensor
        # So, scale raw light values by 1/0.034 as per the datasheet
        ch0 *= 1 / 0.034
        ch1 *= 1 / 0.034

        # Assume we are using the default low gain setting
        # So, scale raw light values by 16 as per the datasheet
        ch0 *= 16;
        ch1 *= 16;

        # Calculate lux based on the ratio as per the datasheet
        if ratio <= 0.5:
            return int((0.0304 * ch0) - ((0.062 * ch0) * ((ch1/ch0) ** 1.4)))
        elif ratio <= 0.61:
            return int((0.0224 * ch0) - (0.031 * ch1))
        elif ratio <= 0.8:
            return int((0.0128 * ch0) - (0.0153 * ch1))
        elif ratio <= 1.3:
            return int((0.00146 * ch0) - (0.00112*ch1))
        else:
            return int(0.0)


class HPD_SGP30():
    def __init__(self):
        self.i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
        self.sensor = adafruit_sgp30.Adafruit_SGP30(self.i2c)
        self.sensor.iaq_init()
        self.sensor.set_iaq_baseline(0x8973, 0x8aae)

    def read(self):
        try:
            return((self.sensor.eCO2, self.sensor.TVOC))
        except:
            return((self.sensor.co2eq, self.sensor.tvoc)) # returns co2eq in ppm and TVOC in ppb

    def read_baseline(self):
        try:
            return((self.sensor.baseline_eCO2, self.sensor.baseline_TVOC))
        except:
            return((self.sensor.baseline_co2eq, self.sensor.baseline_tvoc))
    

class HPD_VL53L1X():
    def __init__(self):
        self.sensor = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=0x29)
        self.sensor.open()

    def read(self):
        self.sensor.start_ranging(1) # 1 = Short range, 2 = Medium Range, 3 = Long Range
        distance = self.sensor.get_distance() # Default returns the distance in mm
        self.sensor.stop_ranging()
        return distance


class HPD_DHT22():
    def __init__(self):
        self.sensor = Adafruit_DHT.DHT22
        self.pin = 17

    def to_f(self, t):
        return t * 9/5.0 + 32
    
    def read(self):
        # h, t = Adafruit_DHT.read_retry(self.sensor, self.pin) # returns humidity in % and temp in celsius
        h, t = Adafruit_DHT.read(self.sensor, self.pin) # returns humidity in % and temp in celsius
        return((h, t))


class Sensors(threading.Thread):
    def __init__(self, read_interval, debug, env_params_root):
        threading.Thread.__init__(self)
        self.debug = debug
        self.gas = HPD_SGP30()
        self.light = HPD_APDS9301()
        self.temp_humid = HPD_DHT22()
        self.dist = HPD_VL53L1X()
        self.read_interval = read_interval
        self.readings = []
        self.env_params_root = env_params_root
        self.env_params_root_date = os.path.join(self.env_params_root, datetime.now().strftime('%Y-%m-%d'))
        self.create_root_env_params_dir()
        self.start()

    def create_root_env_params_dir(self):
          if not os.path.isdir(self.env_params_root):
            os.makedirs(self.env_params_root)
            logging.info('{} created'.format(self.env_params_root))     

    def env_params_dir_update(self):
        start = True
        while 1:
            date_dir = os.path.join(self.env_params_root, datetime.now().strftime('%Y-%m-%d'))
            if not os.path.isdir(date_dir):
                os.makedirs(date_dir)           
            
            self.env_params_root_date = date_dir

            if start:
                hr_dir = os.path.join(self.env_params_root_date, datetime.now().strftime('%H00'))
                if not os.path.isdir(hr_dir):
                    os.makedirs(hr_dir)
                    logging.info('{} created'.format(hr_dir))
                
                self.env_params_dir = hr_dir
                start = False

            if datetime.now().minute % 60 == 0:
                hr_dir = os.path.join(self.env_params_root_date, datetime.now().strftime('%H00'))
                if not os.path.isdir(hr_dir):
                    os.makedirs(hr_dir)
                    logging.info('{} created'.format(hr_dir))

                self.env_params_dir = hr_dir
                time.sleep(60)

    def write_to_file(self, f_path, to_write):
        logging.info('in write_to_file. f_path: {}'.format(f_path))
        # logging.info('data to write: {}'.format(to_write))
        with open(f_path, 'w+') as f:
            json.dump(to_write, f)

    def run(self):
        dir_create = threading.Thread(target=self.env_params_dir_update, daemon=True)
        dir_create.start()
        logging.info('Sensors run')
        first = True
        while True:
            if first:
                while datetime.now().second != 0:
                    pass
                first = False

            if datetime.now().second == 3:
                f_name = datetime.now().strftime('%Y-%m-%d %H%M_env_params.json')
                f_path = os.path.join(self.env_params_dir, f_name)
                time.sleep(1)

            # if datetime.now().second > 0:
            #     written = False
            if datetime.now().second % self.read_interval == 0:
                (h, t) = self.temp_humid.read()
                (co2, tvoc) = self.gas.read()
                (co2_base, tvoc_base) = self.gas.read_baseline()
                self.readings.append({"time": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                                      "light_lux": self.light.read(),
                                      "temp_c": t,
                                      "rh_percent": h,
                                      "dist_mm": self.dist.read(),
                                      "co2eq_ppm": co2,
                                      "tvoc_ppb": tvoc,
                                      "co2eq_base": co2_base,
                                      "tvoc_base": tvoc_base})

                # logging.info('Length of self.readings: {}'.format(len(self.readings)))
                time.sleep(1)
            
            # if datetime.now().second == 59 and not written:
            if datetime.now().second == 59:
                logging.info('Second == 59')
                new_list = self.readings.copy()
                writer = threading.Thread(target=self.write_to_file, args = (f_path, new_list))
                writer.start()
                writer.join()
                self.readings.clear()
                time.sleep(1)
                # written = True

class MyAudio(threading.Thread):
    def __init__(self, audio_root, debug, tape_length):
        threading.Thread.__init__(self)
        self.chunk = 4000
        self.rate = 8000
        self.tape_length = tape_length
        self.format = pyaudio.paInt32
        self.channels = 1
        self.audio_root = audio_root
        self.debug = debug
        self.audio_root_date = os.path.join(self.audio_root, datetime.now().strftime('%Y-%m-%d'))
        self.create_root_audio_dir()
        self.p = pyaudio.PyAudio()
        self.frames = []
        self.stream = False
        self.start()

    def start_stream(self):
        while not type(self.p) == pyaudio.PyAudio:
            self.p = pyaudio.PyAudio()
            time.sleep(1)
            if self.debug:
                print('type(self.p) != pyaudio.PyAudio')
                logging.info('type(self.p) != pyaudio.PyAudio')
            
        while datetime.now().second % self.tape_length != 0:
            pass
        
        logging.info('Starting audio stream.  Time is: ' + datetime.now().strftime('%Y-%m-%d %H:%M'))
        if self.debug:
            print('Starting audio stream.  Time is: ' + datetime.now().strftime('%Y-%m-%d %H:%M'))
        
        # try: 
        if not self.stream:
            if self.debug:
                print('not self.stream')
            self.stream = self.p.open(format = self.format,
                                    channels = self.channels,
                                    rate = self.rate,
                                    input = True,
                                    frames_per_buffer = self.chunk)
        # except:
            if self.debug:
                print('pyaudio.PyAudio() could not be opened.')
            if not self.stream:
                logging.info('pyaudio.PyAudio() could not be opened.')
                if self.debug:
                    print('pyaudio.PyAudio() could not be opened.')
                self.start_stream()
        
    def create_root_audio_dir(self):
        if not os.path.isdir(self.audio_root):
            os.makedirs(self.audio_root)
        
    def audio_dir_update(self):
        while 1:
            date_dir = os.path.join(self.audio_root, datetime.now().strftime('%Y-%m-%d'))
            if not os.path.isdir(date_dir):
                os.makedirs(date_dir)

            self.audio_root_date = date_dir
                
            min_dir = os.path.join(self.audio_root_date, datetime.now().strftime('%H%M'))
            if not os.path.isdir(min_dir):
                os.makedirs(min_dir)
            
            self.audio_dir = min_dir
            
    def write_to_file(self, f_path, to_write):
        wf = wave.open(f_path, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.p.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(to_write))
        wf.close()
        if self.debug:
            print('Attempted to write: {}'.format(f_path))
    
    def run(self):
        dir_create = threading.Thread(target=self.audio_dir_update, daemon=True)
        # dir_create = threading.Thread(target=self.audio_dir_update)
        dir_create.start()

        # Wait for self.audio_dir to exist
        time.sleep(1)

        stream_start = threading.Thread(target=self.start_stream, daemon=True)
        # stream_start = threading.Thread(target=self.start_stream)
        stream_start.start()
        while not self.stream:
            pass
        log_this = True
        while True:
            if datetime.now().minute % 10 == 0 and log_this:
                logging.info('MyAudio thread staying alive')
                log_this = False
            if datetime.now().minute in [1, 11, 21, 31, 41, 51]:
                log_this = True
            while datetime.now().second % self.tape_length != 0:
                pass
            f_name = datetime.now().strftime('%Y-%m-%d %H%M%S_audio.wav')
            f_path = os.path.join(self.audio_dir, f_name) 
            self.frames.clear()
            
            for i in range(0, int(self.rate / self.chunk * self.tape_length)):
                self.frames.append(self.stream.read(self.chunk))

            writer = threading.Thread(target=self.write_to_file, args = (f_path, self.frames))
            writer.start()
            writer.join()
