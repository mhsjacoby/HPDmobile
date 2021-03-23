# Introduction
This repository contains both the client and server side code for the ARPA-E-Sensor project HPDMobile, along with setup guides for configuring the Antsle 'antlets' (VM's).  Each server is a raspberry pi with the following peripherals:
- Raspberry pi camera (photos)
- SPG30 Gas Sensor (TVOC and eCO2)
- DHT22 Sensor (Temp and RH)
- SPH0645LM4H Microphone (sound)
- VL53L1X Distance Sensor (meters)
- APDS-9301 Sensor (lux)

## Glossary
1. antlet: For our understanding, this is essentially a virtual machine which is running on the Antsle.  We have multiple antlets with different functionalities, used to isolate applications.
2. env_params: All data besides photos and sound (TVOC, eCO2, temp, RH, distance, light levels)
3. server = Raspberry pi: since each raspberry pi will be running a streaming video server (UV4L) and server to transfer the env_params, audio, and photos to the Antsle for central storage, it is referred to as a server throughout this project.
4. client: An antlet whose purpose is to connect to one of the servers, capture data points, and store locally on the antsle.  There will be a client antlet for each server.

# Server
Raspberry pi must be running Stretch OS.  Both the camera and I2C must be enabled.  The UV4L Streaming Server module must be running, follow steps [here](https://github.com/corymosiman12/ARPA-E-Sensor/wiki/Setting-up-the-Pi's). Additionally, see the README in the server directory for more details.  The servers will collect env_params at a specified `read_interval` (server.conf), timestamp the data, and store it in memory.  They listen on a specific port `listen_port`, waiting for the client to request data.  Upon request, data will be transferred over a TCP socket.  If the client successfully receives and writes the data to the InfluxDB, the server will clear those readings from memory and begin collecting for the next interval.


# Antsle
The Antsle will contain multiple antlets with different functions:
- 5-6 antlets will be used as the client antlets
- 1 antlet will be used as the USRP antlet

## Influxdb Antlet
This antlet is running at 10.1.1.10 and is a `debian - LXC`.  It contains the influx database.  To install invluxdb on the antlet, copy the `setup_scripts/antsle_influx_setup.sh` into this antlet and run it at the command line.  See the script for more details.

All env_params from the clients are being written to the hpd_mobile database running on this antlet.  Although influxdb doesn't use tables (as in traditional relational databases), it uses what's called a 'measurement', which is essentially similar to a table.  The 'measurement' used for this is also called 'env_params', which can be seen in the MyClient.influx_write method in client.py.  To access the database:
1. ssh into this antlet
2. run `$ influx` at the CLI - now you will be at the influx CLI
3. run `> use hpd_mobile`
4. Now you can make similar queries as you would in a RDBMS.  For instance `> select * from env_params where server_id='S3'`

## Client Antlets
The client antlets will write env_params to the Influxdb Antlet.  They will additionally write photos and audio data to a virtual drive mounted at `/mnt/vdb/` (as specified by the client.conf `img_audio_root` parameter).  400 GB HDD has been allocated for the images and audio 

### Images
Images will be saved under `/mnt/vdb/<server_id>/img/<date>/<%H:%M>`.  The server id will correspond to the id defined in the client.conf file.  There should be 1,440 directories in the `/date` directory (one for every minute of the day).  60 photos should reside inside each of the `/<%H:%M>` directories, one for each second.

### Audio
Audio will be saved under `/mnt/vdb/<server_id>/audio/<date>/<%H:M>`.  The server id will correspond to the id defined in the client.conf file.  There should be 3 wav files in each `<%H:%M>` directories, one for each minute.

## USRP Antlet


# Archive
    # Test run
    Before testing, you must:
    - Have an influxdb running locally on port 8086 with an `hpd_mobile` table
    - Check the client.conf file and change the `root` setting to a spot on your localhost to save images and audio.
        - Dev root: `/Users/corymosiman/hpd_mobile`
        - Prod root: `/mnt/vdb/`


