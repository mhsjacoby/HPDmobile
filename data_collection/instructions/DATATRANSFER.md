# General
This describes the process we used to offload the data from the antlets to external harddrives. 

## Pickling Data
We use pickle to compress the image and audio files for transfer off of the antlets. Images and audio should be in folder of this structure:
- `/mnt/disk3/H3/BS1/img/2019-05/2019-05-01/` ... (one for each day) or `/mnt/disk3/H3/BS1/img/2019-05-01/`
- Make sure hpd_mobile.service is stopped on all antlets and pis.
- I created a network bridge for each of the Antlets.  You can now ssh directly from your computer to the antlet. They were given IP addresses in the CP router in the 192.168.0.20x range (HPD Black)and 192.168.0.21x (HPD Red)  Their hostnames were also changed:

### HPD Black
```
hostname        ip address
BS1-Antlet      192.168.0.201
BS2-Antlet      192.168.0.202
BS3-Antlet      192.168.0.203
BS4-Antlet      192.168.0.204
BS5-Antlet      192.168.0.205
BS6-Antlet      192.168.0.206
```
- You can ssh into each antlet via: `$ ssh root@BS1-Antlet` or `$ ssh root@192.168.0.201`


# Photos, Audio, Logfiles
  
- Make sure hpd_mobile.service is stopped on all antlets and pis: <br />
    `sudo systemctl stop hpd_mobile.service` <br />
    `sudo systemctl disable hpd_mobile.service`
- Move sensor log file from pi to antlet via sftp:<br />
    `sftp pi@192.168.0.10x:/home/pi/sensors_logfile.log /root/`
- Plug external HD into the antsle in one of the blue ports (USB3.0)
- Stop antlet in antman and [enable USB pass through](https://docs.antsle.com/usbdrives/#usb-pass-through). Restart antlet
- SSH into the antlet
- Find connected devices with: <br />
- `sudo fdisk -l` or `lsblk`
- Mount drive with:<br />
     `sudo mount /dev/sda2 /media/externalHD`
- Create subfolder for specific test (only once per test):<br />
    `mkdir /media/externalHD/testxx`
- Move files to external HD:<br />
    `mv /mnt/disk3/BSx /media/externalHD/testxx/`
- Get the logfiles: <br />
    `mv /root/client_logfile.log /media/externalHD/testxx/BSx`<br />
    `mv /root/sensors_logfile.log /media/externalHD/testxx/BSx`
- Unmount drive with: <br />
    `udisksctl unmount -b /dev/sda2`
- Detach with: <br />
    `udisksctl power-off -b /dev/sda2`
- Repeat this for all of the antlets

# Transfering via SFTP
- Now we will begin transferring data via `sftp` from each Antlet directly onto the external disk. 
- We will perform multiple sftp data transfers at the same time. The following paths follow the mounting structure for a mac
- We will transfer photos and audio data separately onto the external disk for each antlet.  You could even split this up by date if needed
- We tell sftp that we want to transfer from A -> B, where A is the location on the antlet, and B is the location on the external disk.  The -r means recursive and the -a option attempts to continue interrupted transfers and only overwrites a file if there are differences in the file (this is just a safety precaution).
- Transfer audio from BS1 to external disk: 
    - `$ sftp -r -a root@192.168.0.201:/mnt/disk3/BS1/audio /Volumes/HPD_Mobile/test5/BS1/`
- Transfer images from BS1 to external disk: 
    - `$ sftp -r -a root@192.168.0.201:/mnt/disk3/BS1/img /Volumes/HPD_Mobile/test5/BS1/`
- Repeat this for all of the antlets
