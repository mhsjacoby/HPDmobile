import socket
from socket import AF_INET, SOCK_STREAM, SOCK_DGRAM
import threading
import os
import sys
import logging
from datetime import datetime, timedelta
import json
import hpd_sensors
import time
import shutil
import subprocess
import psutil

# TODO:
# 1. create class to log system performance (RAM, CPU, disk space)
# 2. Create another class to observe main python process, and count threads
# 3. Check out the OOM killer /var/log/messages
# ^^ Find python libraries for this ^^

# Alpine as potential option for OS

logging.basicConfig(filename='/home/pi/sensors_logfile.log', level=logging.INFO,
                    format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%d-%m-%Y:%H:%M:%S',)


class Server():
    def __init__(self, debug):
        """
        The server class is the main class, and in this instance, the
        main thread that will be executed.  Once initialized,
        the listening socket is opened and created.

        param: settings <class 'dict'>
                    Contains a listen_port,
                    root document directory,
                    sensor read interval, ....
        """
        logging.info('\n\n\t\t\t ##### NEW START #####')
        self.debug = debug
        self.settings = self.import_server_conf()
        self.host = ''
        self.port = int(self.settings['listen_port'])
        self.root = self.settings['root']
        self.audio_root = self.settings['audio_root']
        self.img_root = self.settings['img_root']
        self.env_params_root = self.settings['env_params_root']
        self.stream_type = self.settings['stream_type']
        self.sensors = hpd_sensors.Sensors(
            int(self.settings['read_interval']), self.debug, self.env_params_root)
        self.audio = hpd_sensors.MyAudio(
            self.audio_root, self.debug, self.settings['audio_tape_length'])
        self.audio_checker = MyAudioChecker(
            self.settings['audio_tape_length'], self.settings['audio_root'])
        self.network_monitor = MyNetworkMonitor()
        self.perf_monitor = MyPerformanceMonitor()
        self.create_socket()

    def import_server_conf(self):
        """
        This function is used to import the configuration file from the
        server directory.  The settings are saved as key:value pairs
        and returned.

        TODO: Format data as json, similar to client.py
        """
        try:
            with open('/home/pi/Github/server/server_conf.json', 'r') as f:
                conf = json.loads(f.read())

            return conf

        except Exception as e:
            logging.critical(
                "Unable to read server configuration file.  Exception: {}".format(e))
            logging.critical('Exiting.  System should reboot program')
            sys.exit(1)

    def create_socket(self):
        """
        Create a socket, listen, and wait for connections.  Upon acceptance
        of a new connection, a new thread class (MyThreadedSocket) is spun off with
        the newly created socket.  The thread closes at the end of execution.
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self.host, self.port))
            sock.listen(5)
            print("Listen socket created on port: {}".format(self.port))
            logging.info("Listen socket created on port: {}".format(self.port))
            self.sock = sock
        except socket.error as e:
            logging.critical('Bind failed.  Exception: {}'.format(e))
            logging.critical(
                'Exiting program.  Program should restart from system')
            sys.exit(1)
        log_this = True
        while True:
            if datetime.now().minute % 10 == 0 and log_this:
                logging.info('Thread count: {}'.format(threading.active_count()))
                log_this = False
            if datetime.now().minute in [1, 11, 21, 31, 41, 51]:
                log_this = True
            try:
                # accept() method creates a new socket separate from the
                # main listening socket.
                (client_socket, client_address) = self.sock.accept()
                try:
                    if client_socket:
                        thr = MyThreadedSocket(
                            client_socket, client_address, self.settings, self.sensors, self.debug, self.audio)
                        thr.start()
                        thr.join()
                        print("New connection with: {}".format(client_address))
                except Exception as e:
                    logging.warning(
                        'create_socket excepted after socket accepted. Exception: {}'.format(e))
                    if client_socket:
                        client_socket.close()
            except Exception as e:
                logging.warning(
                    'create_socket function excepted. Exception: {}'.format(e))

# TODO
# class MySensorsChecker(threading.Thread):


class MyAudioChecker(threading.Thread):
    """
    This class is designed to check the number of audio files written 
    to disk for each minute.

    param: 
    """

    def __init__(self, tape_length, audio_root):
        threading.Thread.__init__(self)
        self.tape_length = int(tape_length)
        self.audio_root = audio_root
        self.audio_seconds = [str(x).zfill(2)
                              for x in range(0, 60, self.tape_length)]
        # self.daemon = True
        self.total_missing = 0
        self.start()

    def run(self):
        logging.info('MyAudioChecker run')
        first_check = True
        while True:
            t = datetime.now()
            # Check audio files for previous minute at the 5 second.
            if t.second == 5:
                t_prev = t - timedelta(minutes=1)
                d = t_prev.strftime("%Y-%m-%d")
                hr = t_prev.strftime("%H%M")

                prev_min_audio_dir = os.path.join(self.audio_root, d, hr)
                should_have_files = [os.path.join(prev_min_audio_dir,
                                                  '{} {}{}_audio.wav'.format(d, hr, s)) for s in self.audio_seconds]

                # logging.info('len: {} should_have_files: {}'.format(
                #     len(should_have_files), should_have_files))

                has_files = [os.path.join(prev_min_audio_dir, f) for f in os.listdir(
                    prev_min_audio_dir) if f.endswith('.wav')]

                if len(has_files) == 0 and not first_check:
                    logging.critical(
                        'No audio files found.  Next line runs os._exit(1)')
                    os._exit(1)

                missing = list(set(should_have_files) - set(has_files))
                if len(missing) > 0:
                    self.total_missing += len(missing)
                    logging.warning(
                        'audio missing: {} files'.format(len(missing)))
                    logging.warning(
                        'audio missing these files: {}'.format(missing))

                # Abrupt exit if more than 5 minutes of data missing.
                if self.total_missing > 5*len(should_have_files):
                    logging.critical('self.total_missing = {}.  Next line runs os._exit(1)'.format(
                        self.total_missing))
                    os._exit(1)

                if first_check:
                    first_check = False

                time.sleep(1)


class MyNetworkMonitor(threading.Thread):
    """
    Used to monitor the number of network connections to the server.
    """

    def __init__(self):
        threading.Thread.__init__(self)
        self.AD = "-"
        AF_INET6 = getattr(socket, 'AF_INET6', object())
        self.proto_map = {
            (AF_INET, SOCK_STREAM): 'tcp',
            (AF_INET6, SOCK_STREAM): 'tcp6',
            (AF_INET, SOCK_DGRAM): 'udp',
            (AF_INET6, SOCK_DGRAM): 'udp6',
        }
        self.proc_names = {}
        self.add_proc_names()
        self.base_conns = []
        self.max_t_wait_conns = 0
        self.count_base_conns()
        self.max_conns = len(self.base_conns)
        self.start()

    def add_proc_names(self):
        for p in psutil.process_iter(attrs=['pid', 'name']):
            self.proc_names[p.info['pid']] = p.info['name']

    def count_base_conns(self):
        for c in psutil.net_connections(kind="inet"):
            laddr = "%s:%s" % (c.laddr)
            raddr = ""
            if c.raddr:
                raddr = "%s:%s" % (c.raddr)
            self.base_conns.append({
                "Proto": self.proto_map[(c.family, c.type)],
                "Local Address": laddr,
                "Remote Address": raddr or self.AD,
                "Status": c.status,
                "PID": c.pid or self.AD,
                "Program Name": self.proc_names.get(c.pid, '?')
            })
        logging.info("Number of base connections: {}".format(
            len(self.base_conns)))
        logging.info("Base connections: {}".format(self.base_conns))

    def run(self):
        logging.info('MyNetworkMonitor run')
        while True:
            # Choose weird start time so that other things aren't happening as well...?
            if datetime.now().second == 46:
                # logging.info('MyNetworkMonitor time to check!')
                try:
                    t_wait_conns = []
                    t_wait_conn_count = 0
                    conns = psutil.net_connections(kind="inet")
                    if len(conns) > self.max_conns:
                        self.max_conns = len(conns)
                        logging.info(
                            'Number of connections has increased to: {}'.format(self.max_conns))

                    for c in conns:
                        if c.status == "TIME_WAIT":
                            t_wait_conns.append({
                                "Proto": self.proto_map[(c.family, c.type)],
                                "Local Address": c.laddr,
                                "Remote Address": c.raddr or self.AD,
                                "Status": c.status,
                                "PID": c.pid or self.AD,
                                "Program Name": self.proc_names.get(c.pid, '?')
                            })
                            t_wait_conn_count += 1

                    if t_wait_conn_count > 0:
                        logging.warning(
                            'Number of sockets in TIME_WAIT: {}'.format(t_wait_conn_count))
                        logging.warning('Sockets: {}'.format(t_wait_conns))
                except Exception as e:
                    logging.warning('MyNetworkMonitor excepted: {}'.format(e))

                time.sleep(1)


class MyPerformanceMonitor(threading.Thread):
    """
    Used to monitor the disk space, CPU, and memory of the pi.
    """

    def __init__(self):
        threading.Thread.__init__(self)
        self.disk_threshold = 75
        self.mem_threshold = 25
        self.calc_cpu_range()
        self.start()

    def calc_cpu_range(self):
        cpu = psutil.cpu_freq()
        self.cpu_range = cpu.max - cpu.min

    def run(self):
        logging.info('MyPerformanceMonitor run')
        while True:
            # michaelJordan time
            if datetime.now().second == 23:
                try:
                    # logging.info('MyPerformanceMonitor time to check!')
                    cpu_perc = psutil.cpu_percent()
                    if cpu_perc > 80:
                        m = 'High CPU usage: {}'.format(cpu_perc)
                        logging.warning(m)
                        # print(m)

                    virt_mem = psutil.virtual_memory()
                    if virt_mem.percent <= self.mem_threshold:
                        m = 'High virtual mem usage. Mem available: {}'.format(
                            virt_mem.percent)
                        logging.warning(m)
                        # print(m)

                    swap_mem = psutil.swap_memory()
                    if swap_mem.percent >= self.mem_threshold:
                        m = 'High swap mem usage: {}'.format(swap_mem.percent)
                        logging.warning(m)
                        # print(m)

                    disk_usage = psutil.disk_usage('/')
                    if disk_usage.percent >= self.disk_threshold:
                        m = 'High disk usage: % User disk utilization: {}'.format(
                            disk_usage.percent)
                        # print(m)
                        logging.warning(m)

                    if datetime.now().minute % 5 == 0:
                        logging.info('CPU Perc Usage: {}\tVirt Mem Perc Usage: {}\tSwap Mem Perc Usage: {}\tDisk Perc Usage: {}'.format(
                            cpu_perc, virt_mem.percent, swap_mem.percent, disk_usage.percent))
                except Exception as e:
                    logging.warning(
                        'MyPerformanceMonitor excepted: {}'.format(e))
                time.sleep(1)


class MyThreadedSocket(threading.Thread):
    """
    Instantiate a new thread to manage socket connection with client.
    A multi-threaded server approach likely is unnecessary, but, it's
    good practice.

    param: socket <class 'socket.socket'>
            A newly created socket created by the listen socket
            upon acceptance of new connection.
    param: address
            IP address of client to respond to
    param: settings <class 'dict'>
            Server configuration settings
    param: sensors <class 'hpd_sensors.Sensors'>
            Pointer to master class of sensors.  Allows thread
            to get readings from sensors to send to client.
    """

    def __init__(self, socket, address, settings, sensors, debug, audio):
        threading.Thread.__init__(self)
        self.client_socket = socket
        self.client_address = address
        self.stream_size = 4096
        self.settings = settings
        self.sensors = sensors
        self.debug = debug
        self.audio = audio

    def decode_request(self):
        """
        Each line in the client message is separated by a
        carriage return and newline. The first line is 
        the time the request is sent from the client side.  Additional
        lines specify if client wants env_params, audio directories, or photo
        directories.
        """
        decoded = self.request.split('\r\n')
        self.client_request_time = decoded[0]
        self.client_request = decoded[1]
        if len(decoded) > 2:
            self.dirs_to_delete = decoded[2:]

    def send_sensors(self):
        """
        Create dictionary of readings, along with additional meta data
        client_request_time and server_response_time, which may be useful 
        for debugging.  List of all readings is sent as the "Readings".

        return: <class 'bytes'>
                Encoded byte string ready to stream to client
        """
        to_send = {"Client_Request_Time": self.client_request_time,
                   "Server_Response_Time": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                   "Readings": self.sensors.readings}
        return json.dumps(to_send).encode()

    def my_recv_all(self, timeout=2):
        """
        Regardless of message size, ensure that entire message is received
        from client.  Timeout specifies time to wait for additional socket
        stream.  By default, will use socket passed to thread.

        return: <class 'str'>
                A string containing all info sent.
        """
        # try:
        # make socket non blocking
        self.client_socket.setblocking(0)

        # total data partwise in an array
        total_data = []
        data = ''

        # beginning time
        begin = time.time()
        while 1:
            # if you got some data, then break after timeout
            if total_data and time.time()-begin > timeout:
                break

            # if you got no data at all, wait a little longer, twice the timeout
            elif time.time()-begin > timeout*2:
                break

            # recv something
            try:
                data = self.client_socket.recv(8192).decode()
                if data:
                    total_data.append(data)
                    # change the beginning time for measurement
                    begin = time.time()
                else:
                    # sleep for sometime to indicate a gap
                    time.sleep(0.1)
            except:
                pass
            # except Exception as e:
            #     logging.warning('Exception occured in my_recv_all inner.  Exception: {}'.format(e))
            #     try:
            #         self.client_socket.close()
            #     except:
            #         pass
        # except Exception as e:
        #     logging.warning('Exception occured in my_recv_all_outer.  Exception: {}'.format(e))
        #     try:
        #         self.client_socket.close()
        #     except:
        #         pass

        # join all parts to make final string
        return ''.join(total_data)

    def run(self):
        """
        Process client request, send requested information, and ensure
        data has been received and successfully written to disk on the
        client side.  If success, cached list of sensor readings, i.e.
        self.sensor.readings, is reset back to empty (to reduce
        possibility of overloading server memory).
        """
        # Receive all data from new client and decode
        self.request = self.my_recv_all()
        self.decode_request()

        if self.client_request == "to_remove":
            deleted = []
            try:
                # self.dirs_to_delete is updated in self.decode_request
                for d in self.dirs_to_delete:
                    if os.path.isdir(d):
                        try:
                            shutil.rmtree(d)
                        except:
                            logging.info('Unable to remove dir: {}'.format(d))

                    # Regardless of whether or not it was a directory, if it doesn't exist,
                    # then it is identified as 'deleted'
                    if not os.path.isdir(d):
                        deleted.append(d)

                # Respond to client with the number of directories removed,
                # followed by the names of the directories on the pi.
                temp = [str(len(deleted))]
                for d in deleted:
                    if self.debug:
                        print('Deleted: {}'.format(d))
                    temp.append(d)

                logging.info('Deleted {} dirs'.format(len(deleted)))
                logging.info('Dirs deleted: {}'.format(deleted))

                # Messages always seperated by carriage return, newline
                message = '\r\n'.join(temp)
                
                logging.info('server_delete_response to client: {}'.format(message))
                # Respond to clien
                self.client_socket.sendall(message.encode())

                # Close socket
                self.client_socket.close()
                logging.info("to_remove socket closed, try")

            except Exception as e:
                logging.warning('to_remove excepted.  Exception: {}'.format(e))

            finally:
                if self.client_socket:
                    self.client_socket.close()
                    logging.info("to_remove socket closed, finally")

        # elif self.client_request == 'restart':
        #     try:
        #         dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        #         r = ['Pi to restart.  Time is: {}'.format(dt)]
        #         message = '\r\n'.join(r)
        #         self.client_socket.sendall(message.encode())
        #         self.client_socket.close()

        #         # time.sleep(10)
        #         logging.warning("self.client_request = restart.  Time is: {}".format(dt))
        #         self.subprocess.run("sudo reboot", shell = True)
        #         # subprocess.run("sudo service hpd_mobile restart", shell = True)
        #     except Exception as e:
        #         logging.warning('restart excepted.  Exception: {}'.format(e))
        #         if self.client_socket:
        #             try:
        #                 self.client_socket.close()
        #             except Exception as e:
        #                 logging.info('Unable to close client_socket in restart.  Socket may already be closed.  Exception: {}'.format(e))

        # elif self.client_request == 'restart_img':
        #     try:
        #         dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        #         r = ['Pi to restart UV4L.  Time is: {}'.format(dt)]
        #         message = '\r\n'.join(r)
        #         self.client_socket.sendall(message.encode())
        #         self.client_socket.close()

        #         # time.sleep(10)

        #         logging.warning("self.client_request = restart_img.  Time is: {}".format(dt))
        #         # subprocess.run("sudo reboot", shell = True)
        #         subprocess.run("sudo service uv4l_raspicam stop", shell = True)
        #         time.sleep(2)
        #         subprocess.run("sudo service uv4l_raspicam start", shell = True)

        #     except Exception as e:
        #         logging.warning('restart_img excepted.  Exception: {}'.format(e))
        #         if self.client_socket:
        #             try:
        #                 self.client_socket.close()
        #             except Exception as e:
        #                 logging.info('Unable to close client_socket in restart_img.  Socket may already be closed.  Exception: {}'.format(e))

        # Make sure socket is closed
        self.client_socket.close()


if __name__ == '__main__':
    """
    Upon initialization of the program, the configuration file is read
    in and passed to the Server.  The Server is responsible for gathering
    and caching sensor data until a request is received from a client.
    Depending on the data requested, the Server will either send environmental 
    parameters data or 
    """
    debug = True
    s = Server(debug)
