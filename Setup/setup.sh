#!/bin/bash

# to use: chmod +x computer_setup.sh
# sudo ./computer_setup.sh >> computer_setup_log.txt

# create an overall installation log file
curdir=$(cd `dirname $0` && pwd)
logfile_all="$curdir/computer_setup.log"
rm -f $logfile_all # remove if it already exists

# General Logger simple
log_all(){
	timestamp=$(date +"%Y-%m-%d %k:%M:%S")
	echo "\n$timestamp $1"
	echo "$timestamp $1" >> $logfile_all 2>&1
}

# ----- Basic Update ---- #
sudo apt-get -y update
sudo apt-get -y upgrade
sudo apt dist-upgrade -y
# sudo reboot
log_all "Initial Update Complete"

#-- Install Git -- #
sudo apt-get -y install git
git config --global user.email amarsbars@gmail.com
git config --global user.name Ammar
log_all "Git Installed"

#-- Setup SSH -- #
bash ssh_setup.sh
log_all “SSH setup”

# ---- Create Folders --- #
cd ~/Documents
mkdir Software
sudo chown ammar Software
sudo chgrp ammar Software
mkdir Projects
sudo chown ammar Projects
sudo chgrp ammar Projects
log_all "General Folders Created"

# ---- Install Python Things ---- #
cd $curdir
bash python_setup.sh

# ---- Install Chrome ---- #
cd $curdir
bash chrome_setup.sh

# ---- Prep Install for OpenCV ---- #
cd $curdir
sudo apt-get -y install build-essential
sudo apt-get -y install cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev
sudo apt-get -y install python-dev python-numpy libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libjasper-dev libdc1394-22-dev

#---- Install OpenAI Gym ---- #
cd $curdir
bash openAI_setup.sh

#---- Sublime ----#
cd $curdir
bash sublime_setup.sh


#---- Spotify ----#
cd $curdir
# 1. Add the Spotify repository signing key to be able to verify downloaded packages
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 0DF731E45CE24F27EEEB1450EFDC8610341D9410
# 2. Add the Spotify repository
echo deb http://repository.spotify.com stable non-free | sudo tee /etc/apt/sources.list.d/spotify.list
# 3. Update list of available packages
sudo apt-get -y update
# 4. Install Spotify
sudo apt-get -y install spotify-client


#---- MATLAB ----#
#have to do it manually! - too bad can't use wget

#---- Tensor Flow ---- #

#---- Install Mendeley ----- #
cd $curdir
bash mendeley_setup.sh

#--- OpenRAVE --- #
cd $curdir
bash openrave_new_setup.sh

# --- Docker ---- #
cd $curdir
bash docker_setup.sh

# ---- Pycharm ---- #
cd $curdir
bash pycharm_setup.sh

# ----- TeamViewer ---- #
cd $curdir
bash teamviewer_setup.sh

#---- General ----#
cd $curdir
bash general_packages_setup.sh

sudo apt-get autoremove
sudo apt-get autoclean
