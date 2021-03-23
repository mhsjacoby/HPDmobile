apt update
apt upgrade

# If unable to lock /var/lib/dpkg/, run `$ ps aux | grep apt`, then kill the process with `$ kill [processNumber]

apt install build-essential cmake git pkg-config
apt install libjpeg8-dev libtiff5-dev libjasper-dev libpng12-dev
apt install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev

wget https://bootstrap.pypa.io/get-pip.py
python3 get-pip.py
rm get-pip.py
pip3 install virtualenv virtualenvwrapper

# # virtualenv and virtualenvwrapper
# # nano .bashrc and add the following to bottom
# export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
# export WORKON_HOME=$HOME/.virtualenvs
# source /usr/local/bin/virtualenvwrapper.sh

# source .bashrc

# Create a new virtualenv called 'cv'
mkvirtualenv cv

# When you are in the virtualenv, (cv) should appear at the front now
# You can run `(cv) $ deactivate` to exit out of a virtualenv
# Then run `$ workon cv` to enter back into the virtualenv
# https://virtualenvwrapper.readthedocs.io/en/latest/command_ref.html

# Stay in the virtualenv and run the following
pip install numpy
pip install opencv-python
pip install influxdb
apt update
apt upgrade

# Then we need to setup an ipaddress for the VM.