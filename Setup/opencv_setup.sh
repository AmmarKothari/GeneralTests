
###########################################################
# OpenCV 3.0.0 alpha - installation
# http://opencv.org
###########################################################
# Starting Install
log "Beginning OpenCV 3 Install"

# create logging for openCV
cd SoftwareSource
# Time: Start
dateformat="+%a %b %-eth %Y %I:%M:%S %p %Z"
starttime=$(date "$dateformat")
starttimesec=$(date +%s)

# Current Directory
curdir=$(cd `dirname $0` && pwd)

# create a log file
logfile="$curdir/install-opencv.log"
rm -f $logfile # remove if it already exists

# Ubuntu Upgrade/Update
sudo apt-get update
sudo apt-get upgrade
log "General Ubuntu Update/Upgrade"
 
#----------------------------------------------------------
# Installing OpenCV Dependencies
#----------------------------------------------------------
log "Installing OpenCV Dependencies"
sudo apt-get install build-essential cmake pkg-config libjpeg8-dev libtiff5-dev libjasper-dev libpng12-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libgtk-3-dev libatlas-base-dev gfortran python2.7-dev python3.5-dev

sudo apt-get install libgphoto2-dev libavresample-dev
sudo apt-get install libatlas-base-dev
sudo apt-get install gstreamer1.0-libav
#----------------------------------------------------------
# Install OpenCV
#----------------------------------------------------------
log "Install OpenCV 3.0.0"
FOLDER_NAME="opencv" # Define folder constant

# Create folder
cd ~/Documents/SoftwareSource
mkdir ${FOLDER_NAME}
cd ${FOLDER_NAME} # go to new folder

#download main code from github (https://www.learnopencv.com/install-opencv3-on-ubuntu/)
git clone https://github.com/opencv/opencv.git
cd opencv
git checkout 2b44c0b6493726c465152e1db82cd8e65944d0db
cd ..

# download contrib code from github
git clone https://github.com/opencv/opencv_contrib.git
cd opencv_contrib
git checkout abf44fcccfe2f281b7442dac243e37b7f436d961
cd ..

log "Downloaded OpenCV 3.2"
 
# make build directory
cd opencv
mkdir build
cd build
 
# build with cmake
cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D WITH_TBB=ON -D WITH_V4L=ON -D WITH_QT=ON -D WITH_OPENGL=ON -D INSTALL_PYTHON_EXAMPLES=ON -D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib/modules -D BUILD_EXAMPLES=ON  -D BUILD_opencv_python3=ON ..

# Compile and install
make -j $(nproc)
sudo make install
 
# Adds the path of the OpenCV libraries to the standard Ubuntu library search paths
sudo /bin/bash -c 'echo "/usr/local/lib" > /etc/ld.so.conf.d/opencv.conf'
 
# Updates the Ubuntu default library search paths
sudo ldconfig
log "OpenCV 3.2.0 Installed Successfully!"

#----------------------------------------------------------
# show how long installation took
#----------------------------------------------------------

# Tempo: fim
endtime=$(date "$dateformat")
endtimesec=$(date +%s)

# Mostra tempo gasto com a instalação
elapsedtimesec=$(expr $endtimesec - $starttimesec)
ds=$((elapsedtimesec % 60))
dm=$(((elapsedtimesec / 60) % 60))
dh=$((elapsedtimesec / 3600))
displaytime=$(printf "%02d:%02d:%02d" $dh $dm $ds)
log "Tempo gasto: $displaytime\n"

