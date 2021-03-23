## 2. Semi-Easy Method
This basically follows this [PyImageSearch Post](https://www.pyimagesearch.com/2015/07/20/install-opencv-3-0-and-python-3-4-on-ubuntu/), but is slightly condensed.
1. Update and upgrade packages.
`$ sudo apt update`
`$ sudo apt upgrade`

Note: *If unable to lock /var/lib/dpkg/, run `$ ps aux | grep apt`, then kill the process with `$ kill [processNumber]`*

2. Install pip
`$ wget https://bootstrap.pypa.io/get-pip.py`
`$ sudo python3 get-pip.py`
`$ rm get-pip.py`
`$ pip3 install virtualenv virtualenvwrapper`

3. virtualenv and virtualenvwrapper setup
`$ sudo nano .bashrc` and add the following 3 lines to bottom
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
export WORKON_HOME=$HOME/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh

Exit out of the `.bashrc` file and run at the command line
`$ source .bashrc`

4. Create a new virtualenv called 'cv'
`$ mkvirtualenv cv`

When you are in the virtualenv, (cv) should appear at the front now.  You can run `(cv) $ deactivate` to exit out of a virtualenv.  Then run `$ workon cv` to enter back into the virtualenv.  See here for docs: https://virtualenvwrapper.readthedocs.io/en/latest/command_ref.html

5. Install numpy, opencv, influxdb, imutils
`(cv) $ pip install numpy`
`(cv) $ pip install opencv-python`
`(cv) $ pip install influxdb`
`(cv) $ pip install imutils`
`(cv) $ sudo apt update`
`(cv) $ sudo apt upgrade`

## 3. Long method
This basically follows this [PyImageSearch Post](https://www.pyimagesearch.com/2015/07/20/install-opencv-3-0-and-python-3-4-on-ubuntu/), but with a few modifications.
1. Update and upgrade packages.
`$ sudo apt update`
`$ sudo apt upgrade`

Note: *If unable to lock /var/lib/dpkg/, run `$ ps aux | grep apt`, then kill the process with `$ kill [processNumber]`*

2. Install Requirements to Build OpenCV
`$ sudo apt install build-essential cmake git pkg-config`
`$ sudo apt install libjpeg8-dev libtiff5-dev libjasper-dev libpng12-dev -y`
`$ sudo apt install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev`

3. Install pip
`$ wget https://bootstrap.pypa.io/get-pip.py`
`$ python3 get-pip.py`
`$ rm get-pip.py`
`$ pip3 install virtualenv virtualenvwrapper`

4. virtualenv and virtualenvwrapper setup
`$ nano .bashrc` and add the following 3 lines to bottom
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
export WORKON_HOME=$HOME/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh

Exit out of the `.bashrc` file and run at the command line
`$ source .bashrc`

5. Create a new virtualenv called 'cv'
`$ mkvirtualenv cv`

When you are in the virtualenv, (cv) should appear at the front now.  You can run `(cv) $ deactivate` to exit out of a virtualenv.  Then run `$ workon cv` to enter back into the virtualenv.  See here for docs: https://virtualenvwrapper.readthedocs.io/en/latest/command_ref.html

6. Install numpy, opencv, influxdb, imutils
`(cv) $ pip install numpy`
`(cv) $ pip install opencv-python`
`(cv) $ pip install influxdb`
`(cv) $ pip install imutils`
`(cv) $ apt update`
`(cv) $ apt upgrade`