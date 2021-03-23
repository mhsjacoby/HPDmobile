# Introduction
The following outlines how to install opencv, imutils, and their required dependencies on Ubuntu16.04 KVM for the Antsle.  It took quite a few tries to get opencv working, and the other attempts are documented in the `Archive` of this directory.  This method ONLY WORKS if you have root user privileges.  Anything proceeded by `$` should be run at the command line.  Note that for any of this to work, the Antsle must have an outbound internet connection.

We will use the `root` user for all of the individual antlet setups.  If, at any point, a network error is encountered, simply restart the Antsle.  This typically works.

# Antsle first-time setup
With a new antsle need to add remote origin for github
1. `$ mkdir root/Github`
2. `$ cd root/Github`
3. `$ git init`
4. `$ git remote add origin https://github.com/mhsjacoby/ARPA-E-Sensor.git`
5. `$ git fetch origin`
6. `$ git checkout [current branch]` (current branch should be `master`)

# Antlet setup
1. Create a new `Ubuntu16.04 - KVM` antlet through antman.  I have been using `Inherit` compression.

2. Open up the console and enable non-root ssh. Follow this guide [here](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/6/html/v2v_guide/preparation_before_the_p2v_migration-enable_root_login_over_ssh)
- Login as `root` and pw: `antsle`
- Default users and passwords can be found [here](https://docs.antsle.com/availtemplates/)
- To test if this worked, close out of the console and try to ssh into the Antlet as the root user.  If you are able to, then it has worked!
- Perform all OpenCV setup by ssh'ing in as the root user.

3. Mount a new virtual drive with 400 GB HDD space.  Name it `vdb`, then follow this guide [here](https://docs.antsle.com/drives/).
- IMPORTANT: use the hdd zpool, NOT the antlets zpool!!!
- If it is the first drive created, the target name should always be `vdb`
- Regardless of the target name, when we need to create a new directory, name it `/mnt/vdb`, i.e. perform `mkdir /mnt/vdb`.
- Follow the rest of the guide, only performing the Debian/Ubuntu steps.

4. install pillow and scipy packages for python (for pickling audio and images)
- `pip install Pillow`
- `pip install scipy`


## Rename host (need to change in two files)
`$ sudo nano /etc/hostname`, and change name to 'BS1-Antlet' or similar then reboot.

Go to: `$ sudo nano /etc/hosts` 
and make sure the line with `127.0.1.1` looks like:
```127.0.1.1          <our_hostname>```
where `<our_hostname>` would be BS3-Antlet or whatever.

Check that the date is correct:
- `$ date`, should print stuff out.  will likely say PST.  Need to change to MST
- `$ timedatectl set-timezone "America/Denver"`


# OpenCV Setup
This is a combination of the update posted in [this install guide](https://medium.com/@debugvn/installing-opencv-3-3-0-on-ubuntu-16-04-lts-7db376f93961), addressing the [errors noted here](https://stackoverflow.com/questions/47113029/importerror-libsm-so-6-cannot-open-shared-object-file-no-such-file-or-directo).  Note that parts 1 and 2 are just to get the virtualenv setup.  Once we are in the virtualenv, it follows the first install guide.

1. Install pip
- `wget https://bootstrap.pypa.io/get-pip.py`
- `python3 get-pip.py`
- `rm get-pip.py`
- `pip3 install virtualenv virtualenvwrapper`

2. virtualenv and virtualenvwrapper setup
- `nano .bashrc` and add the following 3 lines to bottom
- `export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3`
- `export WORKON_HOME=$HOME/.virtualenvs`
- `source /usr/local/bin/virtualenvwrapper.sh`

Exit out of the `.bashrc` file and run at the command line:
- `source .bashrc`

3. Create a new virtualenv called 'cv':
- `mkvirtualenv cv`

When you are in the virtualenv, (cv) should appear at the front now.  You can run `(cv) $ deactivate` to exit out of a virtualenv.  Then run `$ workon cv` to enter back into the virtualenv.  See here for docs: https://virtualenvwrapper.readthedocs.io/en/latest/command_ref.html

4. Install OpenCV (+ 3 dependencies), influxdb client, imutils
- `(cv) $ pip install opencv-python`
- `(cv) $ apt update && apt upgrade`
- `(cv) $ apt install -y libsm6 libxext6`
- `(cv) $ apt install -y libxrender-dev`
- `(cv) $ pip install imutils`
- `(cv) $ pip install pysftp`

5. ssh from antlet vm to correct raspberry pi, should look something like this:
- `ssh pi@192.168.0.101`

6. Copy client folder from root profile
- `(cv) $ sftp -r root@192.168.0.50:Github/client .`

# Set-up antlet for file transfer
This allows us to mount the external drive directly to the antlet and move or copy the audio and image files

1. Install udisks2 with: `apt install udisks2`
2. Install exfat file system with: `sudo apt-get install exfat-fuse exfat-utils`
3. Install NFS softwarre with: `sudo apt install nfs-kernel-server`
4. Start service with: `sudo systemctl start nfs-kernel-server.service`
5. Create directory to mount external to with: `mkdir /media/externalHD`


# Create the service
This is the same as the service on the pi, except we add the conencted server: Replace [server_id] with BS3 or whatever is the id of the server this antlet is connecting to. After setting up we need to disable the service until we are ready to deploy.  This eliminates the service from running (collecting data) when we aren't testing / depoloying.


1. `$ sudo touch /lib/systemd/system/hpd_mobile.service`
2. `$ sudo nano /lib/systemd/system/hpd_mobile.service` and add the following:

```
[Unit]
Description=Service to start Github/client/client.py on boot from venv
After=multi-user.target

[Service]
Type=simple
ExecStart=/root/.virtualenvs/cv/bin/python /root/client/client.py [server_id]
Restart=always

[Install]
WantedBy=multi-user.target
```

3. Reload service daemon: `$ sudo systemctl daemon-reload`
4. Enable the service by default: `$ sudo systemctl enable hpd_mobile.service`
5. Reboot the pi: `$ sudo reboot`
6. Log back in and check if the service is running: `$ sudo systemctl status hpd_mobile.service`
7. Stop the service: `$ sudo systemctl stop hpd_mobile.service`
8. Disable the service to prevent it from starting on boot: `$ sudo systemctl disable hpd_mobile.service`

# Setup network bridge

Follow steps [here](https://docs.antsle.com/bridgevnic/#configure-ip-address)