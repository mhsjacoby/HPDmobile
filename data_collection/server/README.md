# Intro
This page is meant to describe the process for getting sensor hubs configured with necessary packages and dependencies. 

The pi must be running the `stretch` OS (didn't work when I tried on `jessie`).  Type `$ cat /etc/os-release` to check OS version.  If not, follow the guide [here](https://www.raspberrypi.org/documentation/installation/noobs.md).

For the most part, this wiki will follow the install [here](https://www.linux-projects.org/uv4l/installation/).  I have condensed it to only the commands we need below.  This will require an internet connection on the pi.

# First Steps
When setting up for the first time install Debian OS and make sure to select `US Keyboard setup`

When prompted change the pi password to `arpa-e`

On first log-on, initially connect to the `IBR600B-3f4` WiFi network. Then for the remainder of the steps connect to the UCB Wireless network. Instructions at the end for setting preferred network. NOTE: After each reboot you will have to reset the wifi network to UCB Wireless.

Enable camera and other peripherals.  Run `$ sudo raspi-config`, then go to `Interfacing Options` and enable: <br />
    - Camera <br />
    - SPI <br />
    - I2C <br />
    - SSH <br />

## If need to reset time/date:
Run `$ date` at cmd line, and if it says old date, run: `$ timedatectl`,  then run `$ date` again.

If it still says old data then set manually with: <br />
`$ sudo date --set='TZ="America/Denver" 25 Dec 2018 18:09' ` (with current time and date)

## Rename pi (need to change in two files on pi)
`$ sudo nano /etc/hostname`, and change name to 'BS1' or similar then reboot.

Go to: `$ sudo nano /etc/hosts` 
and make sure the line with `127.0.1.1` looks like:
```127.0.1.1          <our_hostname>```
where `<our_hostname>` would be BS3 or whatever.


## Remove unnecessary packages
To free up some space and limit the number of packages we will eventually install, we are going to remove our wolfram and libreoffice packages:
1. `$ sudo apt-get purge wolfram-engine` This might not be installed
2. `$ sudo apt-get clean && sudo apt-get autoremove`
3. `$ sudo apt-get remove --purge libreoffice*`
4. `$ sudo apt-get clean && sudo apt-get autoremove`
5. `$ sudo reboot`
6. `$ sudo apt update && sudo apt upgrade`

# Download and Set-up Packages and Dependencies 

## Set-up UV4L on the Pi
This section describes getting the UV4L library up and running on a Raspberry Pi.  UV4L allows the pi to act as a streaming video server, which can be connected to using `OpenCV` on a client side application.

Open a terminal and type:<br />
`$ curl http://www.linux-projects.org/listing/uv4l_repo/lpkey.asc | sudo apt-key add -` <br />

Add the following line to the end of the `sources.list` file by typing: <br />
`$ sudo nano /etc/apt/sources.list` at the command line

Then add at the end of the file: 
`deb http://www.linux-projects.org/listing/uv4l_repo/raspbian/stretch stretch main`

Next, update, fetch, and install uv4l packages: <br />

`$ sudo apt-get update` <br />
`$ sudo apt-get install uv4l uv4l-raspicam` <br />

We want the driver to load at boot, so type the following <br />
`$ sudo apt-get install uv4l-raspicam-extras` <br />

Install the front-end server: <br />
`$ sudo apt-get install uv4l-server uv4l-uvc uv4l-xscreen uv4l-mjpegstream uv4l-dummy uv4l-raspidisp` <br />

Reboot the pi. <br />

By default, the streaming video server will run on port 8080.  You should now be able to access the video server from a web-browser by typing in `localhost:8080`.  Clicking on the MJPEG/Stills stream will show you the stream.  The `Control Panel` tab will allow you to adjust settings.  I found that reducing the resolution to 3x our target (112x112 is target of WISPCam), so 336x336, gives us minimal lag time.

## Raspicam Options
Edit the raspicam default options to use a lower resolution and framerate and use mjpeg streaming.  Set the resolution to 336x336 and the framerate to 2fps.  This is done via:
`$ sudo nano /etc/uv4l/uv4l-raspicam.conf`

Find the section labeled `raspicam driver options`.  In this section, modify :
```
encoding = mjpeg
width = 336
height = 336
framerate = 2
```

Restart the UV4L server, and you should see these defaults change.  This command can be run at anytime to restart the UV4L server.
`$ sudo service uv4l_raspicam restart`

## Streaming Over the Network
Now, to test the pi running over the network:
1. Connect the pi to on our network.
2. Check the IP address of the pi using `$ ifconfig`.
3. Connect your computer to the same network, and access at the browser through: `[piIpAddress]:8080`, i.e. `192.168.1.104:8080`.  You should now have the same stuff available as if you were accessing it through the localhost.

# Environment Setup
This is a combination of the update posted in [this install guide](https://medium.com/@debugvn/installing-opencv-3-3-0-on-ubuntu-16-04-lts-7db376f93961), addressing the [errors noted here](https://stackoverflow.com/questions/47113029/importerror-libsm-so-6-cannot-open-shared-object-file-no-such-file-or-directo).  Note that parts 1 and 2 are just to get the virtualenv setup.  Once we are in the virtualenv, it follows the first install guide.

## Install pip
1. `$ wget https://bootstrap.pypa.io/get-pip.py `
2. `$ sudo python3 get-pip.py`
3. `$ rm get-pip.py`
4. `$ sudo pip3 install virtualenv virtualenvwrapper`

## virtualenv and virtualenvwrapper setup
1. `$ nano .bashrc` and add the following 3 lines to bottom
```
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
export WORKON_HOME=$HOME/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh
```

Exit out of the `.bashrc` file and run at the command line:
2. `$ source .bashrc`

Create a new virtualenv called 'cv'
3. `$ mkvirtualenv cv`

## OpenCV Setup
When you are in the virtualenv, (cv) should appear at the front now.  You can run `(cv) $ deactivate` to exit out of a virtualenv.  Then run `$ workon cv` to enter back into the virtualenv.  See here for docs: https://virtualenvwrapper.readthedocs.io/en/latest/command_ref.html

Install OpenCV (+ dependencies) and imutils
1. `(cv) $ pip install opencv-python`
2. `(cv) $ sudo apt update && sudo apt upgrade`
3. `(cv) $ sudo apt install -y libsm6 libxext6`
4. `(cv) $ sudo apt install -y libxrender-dev`
5. `(cv) $ pip install imutils`

# Install Sensor Specific Libraries
## [Circuit Python](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi)

1. `(cv) $ pip install --upgrade setuptools`
2. `(cv) $ pip install RPI.GPIO==0.6.3`
3. `(cv) $ pip install adafruit-blinka`

## [DHT Sensor](https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/software-install-updated)
1. `(cv) $ git clone https://github.com/adafruit/Adafruit_Python_DHT.git`
2. `(cv) $ sudo apt-get update && sudo apt-get install build-essential python-dev python-openssl`
3. `(cv) $ cd Adafruit_Python_DHT/`
4. `(cv) $ python setup.py install`
5. `(cv) $ cd .. && rm -r Adafruit_Python_DHT/`

## [SGP30](https://learn.adafruit.com/adafruit-sgp30-gas-tvoc-eco2-mox-sensor/circuitpython-wiring-test)
1. `(cv) $ pip install adafruit-circuitpython-sgp30`

## VL53L1X
1. `(cv) $ pip install VL53L1X==0.0.2`

Check out [this post](https://github.com/pimoroni/vl53l1x-python/commit/8e8a29e19c4965219eff5baac085f49502503045) and change code to match accordingly.  If all steps have been followed correctly, code should be in:

`/home/pi/.virtualenvs/cv/lib/python3.5/site-packages/VL53L1X.py`

type:
`$ sudo nano /home/pi/.virtualenvs/cv/lib/python3.5/site-packages/VL53L1X.py` <br />

### NOTE: When copy/pasting from the link the "try" line gets indented. Make sure to remove indent manually.

## NUMPY
May have trouble importing numpy. To fix try this:
`sudo apt-get install libatlas-base-dev`

## [I2S Configuration](https://learn.adafruit.com/adafruit-i2s-mems-microphone-breakout/raspberry-pi-wiring-and-test)

### important: Deactivate your virtualenv: <br />
`(cv) $ deactivate`

1. Turn on i2s support by editing /boot/config.txt with: <br />
`$ sudo nano /boot/config.txt` <br />
Uncomment `#dtparam=i2s=on` <br />

2. Make sure sound support is enabled in the kernal with: <br />
`$ sudo nano /etc/modules` <br />
Add `snd-bcm2835` on its own line as shown below <br />

<img src="https://cdn-learn.adafruit.com/assets/assets/000/040/621/large1024/sensors_Screen_Shot_2017-04-03_at_11.04.57_AM.png?1491243865" width="600">


Reboot with `$ sudo reboot` <br />

3. Once rebooted confirm that the mdoule is loaded with: <br />
 `$ lsmod | grep snd` <br />

<img src="https://cdn-learn.adafruit.com/assets/assets/000/040/622/original/sensors_Screen_Shot_2017-04-03_at_11.06.56_AM.png?1491244026" width="600">


### Kernal Compiling
Now we manually compile to i2s support
4. Install the compilation dependencies <br />
`$ sudo apt-get install git bc libncurses5-dev` <br />

5. Download kernel source and compile <br />
`$ sudo wget https://raw.githubusercontent.com/notro/rpi-source/master/rpi-source -O /usr/bin/rpi-source` <br />
`$ sudo chmod +x /usr/bin/rpi-source` <br />
`$ /usr/bin/rpi-source -q --tag-update` <br />
`$ rpi-source --skip-gcc` <br />
This last part may take 15 minutes or so <br />

Now compile i2s support
6. `$ sudo mount -t debugfs debugs /sys/kernel/debug` <br /> 
This may already be done and will say - mount: debugs is already mounted. Keep going <br />

7. Make sure the module name is: `3f203000.i2s`  by typing: `$ sudo cat /sys/kernel/debug/asoc/platforms`

<img src="https://cdn-learn.adafruit.com/assets/assets/000/040/624/original/sensors_Screen_Shot_2017-04-03_at_11.40.14_AM.png?1491244426" width="600">


8. Download the module written by Paul Creaser <br />
`$ git clone https://github.com/PaulCreaser/rpi-i2s-audio` <br />
`$ cd rpi-i2s-audio` <br />

9. Compile the module with <br />
`$ make -C /lib/modules/$(uname -r )/build M=$(pwd) modules` <br />
`$ sudo insmod my_loader.ko` <br />

10. Verify that the module was loaded: <br />
`$ lsmod | grep my_loader` <br />
`$ dmesg | tail` 

<img src="https://cdn-learn.adafruit.com/assets/assets/000/045/983/original/sensors_insmod.png?1504203051" width="750">

Note that on the Pi 3 you'll see `asoc-simple-card asoc-simple-card.0: snd-soc-dummy-dai <-> 3F203000.i2s mapping ok` on the last line 

11.  Set to autoload on startup: <br />
`$ sudo cp my_loader.ko /lib/modules/$(uname -r)` <br />
`$ echo 'my_loader' | sudo tee --append /etc/modules > /dev/null` <br />
`$ sudo depmod -a` <br />
`$ sudo modprobe my_loader` <br />
`$ sudo reboot`


## PyAudio
activate virtual environment with  `workon cv`
1. `(cv) $ apt-get install portaudio19-dev`
2. `(cv) $ pip install PyAudio==0.2.11`

## Others
1. `(cv) $ pip install circuitpython-build-tools==1.1.5`
2. `(cv) $ pip install smbus2==0.2.1`

# Other things:
## Configure Github on pi:
1. `$ mkdir /home/pi/Github`
2. `$ cd /home/pi/Github`
3. `$ git init`
4. `$ git remote add origin https://github.com/corymosiman12/ARPA-E-Sensor`
5. `$ git fetch origin`
6. `$ git checkout Maggie-branch`

You will need to add in your credentials to the git manager to pull from Github


## Set Cradlepoint as preferred network and set priority
Make sure that the cradlepoint network is at top priority (i.e. it will join it first out of all other networks) by editing:
 `$ sudo nano /etc/wpa_supplicant/wpa_supplicant.conf`.  It should resemble:

```
network={
ssid="IBR600B-3f4"
psk="443163f4"
priority=1
key_mgmt=WPA-PSK
}
```

`$ sudo reboot` Check that it has joined the CP network.

## Create HPD_mobile service
A service basically allows us to run a script immediately on boot without having to enter any commands.

We will want to make sure that the services work on all of the Pi's, but we need to disable them until we are ready to deploy.  This eliminates the service from running (collecting data) when we aren't testing / depoloying. After we go through the following, make sure to run `sudo systemctl disable hpd_mobile.service`, which will prevent it from starting on boot.

1. On the pi, run the following to create a new file: `$ sudo touch /lib/systemd/system/hpd_mobile.service`
2. Edit that file by running `$ sudo nano /lib/systemd/system/hpd_mobile.service` and add the following:

```
[Unit]
Description=Service to start Github/server/server.py on boot from venv
After=multi-user.target

[Service]
Type=simple
ExecStart=/home/pi/.virtualenvs/cv/bin/python /home/pi/Github/server/server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

3. Reload service daemon: `$ sudo systemctl daemon-reload`
4. Enable the service by default: `$ sudo systemctl enable hpd_mobile.service`
5. Reboot the pi: `$ sudo reboot`
6. Check if the service is running: `$ sudo systemctl status hpd_mobile.service`
7. Stop the service: `$ sudo systemctl stop hpd_mobile.service`
8. Disable the service to prevent it from starting on boot: `$ sudo systemctl disable hpd_mobile.service`


## Set up SSH
SSH from Antlet to pi atleast 1x. Upon SSH, you will enable trust between antlet and pi, and will therefore be able to use the `pysftp` library.