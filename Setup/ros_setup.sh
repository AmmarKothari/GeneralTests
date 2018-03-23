# ---- Install ROS ---- #
sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
sudo apt-key adv --keyserver hkp://ha.pool.sks-keyservers.net:80 --recv-key 421C365BD9FF1F717815A3895523BAEEB01FA116
sudo apt-get -y update
sudo apt-get -y upgrade
sudo apt-get -y install  libxss1 libappindicator1 libindicator7
sudo apt-get -y install ros-kinetic-desktop-full python-pip
log_all "ROS Packages Installed"

sudo rosdep init
rosdep update
echo ""
echo "#adding ROS Source File"
echo "source /opt/ros/kinetic/setup.bash" >> ~/.bashrc
sudo apt-get -y install python-rosinstall ros-kinetic-turtlebot* python-wstool

mkdir -p ~/catkin_ws/src
log_all "ROS Setup and Settings Complete"

#---- ROS Packages ----#
sudo apt-get -y install ros-kinetic-usb-cam

source ~/.bashrc
rospack profile

#opening ports for remote control (should have been done when setting up SSH)
sudo ufw allow 22
sudo ufw allow 11311