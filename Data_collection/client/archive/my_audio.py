import pysftp
import threading
import os
import logging
from datetime import datetime, timedelta
import time

logging.basicConfig(filename = 'MyAudio_logfile.log', level = logging.DEBUG,
                    format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%d-%m-%Y:%H:%M:%S',)

class MyAudio(threading.Thread):
    def __init__(self, audio_root, pi_ip_address, pi_img_audio_root):
        threading.Thread.__init__(self)
        logging.info('Initializing MyAudio')
        # self.setDaemon(True)
        self.audio_root = audio_root
        self.audio_root_date = os.path.join(self.audio_root, datetime.now().strftime('%Y-%m-%d'))
        self.pi_ip_address = pi_ip_address
        self.pi_audio_root = '/home/pi/audio'
        self.pi_audio_root_date = os.path.join(self.pi_audio_root, datetime.now().strftime("%Y-%m-%d"))
        self.to_retrieve = []
        self.successfully_retrieved = []
        self.start()

    def audio_dir_update(self):
        while True:
            date_dir = os.path.join(self.audio_root, datetime.now().strftime("%Y-%m-%d"))
            if not os.path.isdir(date_dir):
                os.makedirs(date_dir)
                self.audio_root_date = date_dir
                print('Created: {}'.format(date_dir))

            min_dir = os.path.join(self.audio_root_date, datetime.now().strftime('%H%M'))
            if not os.path.isdir(min_dir):
                os.makedirs(min_dir)
                t = datetime.now() - timedelta(minutes = 1)
                prev_min_dir = os.path.join(self.audio_root_date, t.strftime('%H%M'))
                self.audio_dir = prev_min_dir
                print('Created: {}'.format(min_dir))

    def run(self):
        dir_create = threading.Thread(target=self.audio_dir_update)
        dir_create.start()

        while True:
            if datetime.now().second == 0:
                time.sleep(10)
                t = datetime.now() - timedelta(minutes = 1)
                pi_audio_dir = os.path.join(self.pi_audio_root, t.strftime('%Y-%m-%d'), t.strftime('%H%M'))
                logging.debug('Transferring files from: {}\tTo: {}'.format(pi_audio_dir, self.audio_dir))
                self.to_retrieve.append((pi_audio_dir, self.audio_dir))
                try:
                    with pysftp.Connection(self.pi_ip_address, username='pi', password='sensor') as sftp:
                        for item in self.to_retrieve:
                            try:
                                sftp.get_d(item[0], item[1], preserve_mtime=True)
                                ind = self.to_retrieve.index(item)
                                self.successfully_retrieved.append(self.to_retrieve.pop(ind))
                                logging.info('Successfully retrieved {}'.format(pi_audio_dir))
                                
                            except FileNotFoundError as no_file_error:
                                logging.critical('File not found on Server.  No way to retrieve.')
                                ind = self.to_retrieve.index(item)
                                self.to_retrieve.pop(ind)

                except (ConnectionAbortedError, ConnectionError, ConnectionRefusedError, ConnectionResetError) as conn_error:
                    logging.warning('Network connection error: {}'.format(conn_error))