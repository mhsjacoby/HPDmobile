import cv2
from datetime import datetime, timedelta
import os
import pickle
import logging
import time
import threading
import imutils
from imutils.video import WebcamVideoStream
import numpy as np

# TODO:
# 1. Add error checking and logging to script
# 2. Make sure script works when connected over local wLAN through linksys router

# Initialize camera.  The pi uv4l server must be running at the defined IP address
# and port number specified below.  The path: /stream/video.mjpeg can be found in the 
# pi's 192.168.0.4:8080/info

logging.basicConfig(filename = 'MyPhoto2_logfile.log', level = logging.DEBUG,
                    format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%d-%m-%Y:%H:%M:%S',)

class MyPhoto2(threading.Thread):
    def __init__(self, img_root, pi_ip_address, stream_type):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        print("Initializing MyPhoto2 class")
        self.img_root = img_root
        self.img_root_date = os.path.join(self.img_root, datetime.now().strftime("%Y-%m-%d"))
        self.pi_ip_address = pi_ip_address
        self.stream_type = stream_type
        self.video_status = False
        self.create_dir(os.path.join(self.img_root, datetime.now().strftime("%Y-%m-%d %H%M")))
        self.connect_to_video()
        self.start()
            
    def connect_to_video(self):
        # Select the stream type based on that specified in server.conf
        if self.stream_type == "mjpeg":
            stream_path = "http://" + self.pi_ip_address + ":8080/stream/video.mjpeg"
        elif self.stream_type == "h264":
            stream_path = "http://" + self.pi_ip_address + ":8080/stream/video.h264"
        elif self.stream_type == "jpeg":
            stream_path = "http://" + self.pi_ip_address + ":8080/stream/video.jpeg"
        
        # Attempt to start the video stream
        self.cam = WebcamVideoStream(stream_path).start()

        # Keep attempting to open the video stream until it is opened
        while not self.cam.stream.isOpened():
            self.cam = WebcamVideoStream(stream_path).start()
            self.video_status = False
            logging.warning("Unable to connect to video")
            time.sleep(1)
        
        # Set the video status to true
        self.video_status = True
        logging.info("Connected to video stream")

    def create_dir(self, new_dir):
        if not os.path.isdir(new_dir):
            os.makedirs(new_dir)
            self.img_dir = new_dir
        elif os.path.isdir(new_dir):
            self.img_dir = new_dir

    def img_dir_update(self):
        # This function is run in a separate thread to continuously create a new directory for each day, and for each minute.
        while 1:
            date_dir = os.path.join(self.img_root, datetime.now().strftime("%Y-%m-%d"))
            if not os.path.isdir(date_dir):
                os.makedirs(date_dir)
                self.img_root_date = date_dir
            
            min_dir = os.path.join(self.img_root_date, datetime.now().strftime("%H%M"))
            if not os.path.isdir(min_dir):
                os.makedirs(min_dir)
                self.img_dir = min_dir


    def run(self):
        dir_create = threading.Thread(target=self.img_dir_update)
        dir_create.start()
        
        while 1:
            f_name = datetime.now().strftime("%Y-%m-%d %H%M%S_photo.png")
            f_path = os.path.join(self.img_dir,f_name)

            # Only capture a photo if it doesn't already exist
            if not os.path.isfile(f_path):
                if not len(os.listdir(self.img_dir)) >= 60:
                    img = False
                    img = self.cam.read()
                    if type(img) is not np.ndarray:
                        logging.warning('Camera read did not return image.  Attempting to restart video connection')
                        self.video_status = False
                        self.connect_to_video()
                    # if capture_status:
                    elif type(img) is np.ndarray:
                        try:
                            # Convert image to greyscale
                            img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

                            # Write to disk
                            cv2.imwrite(f_path, img)
                            if datetime.now().minute == 0:
                                logging.info("Created file: {}".format(f_path))

                        except Exception as e:
                            logging.warning("Unable to convert to grayscale and write to disk.  Error: {}.  File: {}\tAttempting to restart video connection".format(e, f_name))
                            # logging.info("Attempting to restart video connection")
                            self.video_status = False
                            self.connect_to_video()
                            # logging.CRITICAL("Unable to convert to grayscale and write to disk.  Error: {}.  File: {}".format(e, fname))