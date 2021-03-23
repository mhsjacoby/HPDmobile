# General
All services on the raspberry pi's and antlet VM's should always be STOPPED before powering off the devices:
- `$ sudo systemctl stop hpd_mobile.service`

# Steps
1. Plug the cradlepoint router in at the home in a central location.
2. Plug in and power up each of the individual raspberry pi's.
3. Plug in and power up the antsle.
4. ssh into all raspberry pi's and antlet VM's simultaneously (remember, you MUST ssh into `ssh root@hpdblack`, then once in there, `ssh root@10.1.1.101` for example to get into the antlet)

## Raspberry Pi
For each raspberry pi:
1. Start the service:
- `$ sudo systemctl start hpd_mobile.service`
2. Check the status.  You will likely get the following errors:
```
Nov 20 19:56:05 BS1 python[19148]: ALSA lib confmisc.c:1281:(snd_func_refer) Unable to find definition 'defaults.bluealsa.device'
Nov 20 19:56:05 BS1 python[19148]: ALSA lib conf.c:4528:(_snd_config_evaluate) function snd_func_refer returned error: No such file or directory
Nov 20 19:56:05 BS1 python[19148]: ALSA lib conf.c:4996:(snd_config_expand) Args evaluate error: No such file or directory
Nov 20 19:56:05 BS1 python[19148]: ALSA lib pcm.c:2495:(snd_pcm_open_noupdate) Unknown PCM bluealsa
Nov 20 19:56:05 BS1 python[19148]: ALSA lib confmisc.c:1281:(snd_func_refer) Unable to find definition 'defaults.bluealsa.device'
Nov 20 19:56:05 BS1 python[19148]: ALSA lib conf.c:4528:(_snd_config_evaluate) function snd_func_refer returned error: No such file or directory
Nov 20 19:56:05 BS1 python[19148]: ALSA lib conf.c:4996:(snd_config_expand) Args evaluate error: No such file or directory
Nov 20 19:56:05 BS1 python[19148]: ALSA lib pcm.c:2495:(snd_pcm_open_noupdate) Unknown PCM bluealsa
Nov 20 19:56:05 BS1 python[19148]: connect(2) call to /tmp/jack-0/default/jack_0 failed (err=No such file or directory)
Nov 20 19:56:05 BS1 python[19148]: attempt to connect to server failed
```
4. This is ok, as long as audio files are being recorded.  Check that they are being recorded:
- `$ ls /home/pi/audio/...` fill in the rest to make sure that there are files in the directories (they will timestamp every 20 seconds)
- Sometimes the microphone will not be working.  In that case, just stop the service, then restart the service.  Reboot the pi if all else fails.  It will start, it may just not work the first time.
5. Make sure that the UV4L video server is up and running.  From your computer, `192.168.0.101:8080` for example.  If it is not running: `$ sudo service uv4l_raspicam restart`

## Antlets
1. Let the raspberry pi's run for atleast 1 minute each.
2. SSH into antlet either directly with `ssh root@192.168.0.201` or into antlse first with `ssh 192.168.0.120`, then antlet with `$ ssh root@10.1.1.101`
3. Start virtual environment: `$ workon cv`
4. Rather than starting the service, just run the data collections program as a normal program first to make sure everything looks good:
- `(cv) $ pwd` should be in /root/client/
- `(cv) $ clear && python client.py SERVER_ID` where SERVER_ID is BS1, BS5, etc.
- It will spit out a whole bunch of stuff.  Let it run for a minute or two and the console readings will begin to make sense.  If all is working, the console will begin spitting out stuff like this:
```
Retriever updater running
Thread started to get: ('/home/pi/audio/2018-11-20/2026', '/mnt/vdb/BS1/audio/2018-11-20/2026')
img missing: 0 files
specifically these files: []
audio missing: 0 files
specifically these files: []
Successfully retrieved /home/pi/audio/2018-11-20/2026
```
## Updating code on the antlets
If the code needs to be updated, do this by first brining it to the antsle, then from the antsle to the antlet.

1. ssh into the antsle from the command line: 
`$ ssh root@192.168.0.120`
2. Navigate to the `root/Github` directory
3. pull new code: `$ git pull origin img_client_side`
4. ssh into the antlet now with `$ ssh root@10.1.1.101`
5. Make sure in `/root` directory with `$ pwd` 
6. `sftp -r 192.168.0.120:Github/client .` brings code from antles to antlet



