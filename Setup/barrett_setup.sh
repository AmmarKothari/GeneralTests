cd ~/Documents/Software
git clone git@github.com:BenBlumer/WAMPy.git

echo "" >> ~/.bashrc
echo "#adding Barrett WAMPy Path" >> ~/.bashrc
export Barrett_WAMPy_DIR=$(pwd)
echo "export ROS_PACKAGE_PATH=$Barrett_WAMPy_DIR:${ROS_PACKAGE_PATH}" >> ~/.bashrc

git clone git@github.com:BenBlumer/catkin-barrett-ros-pkg.git



git clone git@github.com:BarrettTechnology/libbarrett.git
cd libbarrett
mkdir build
cd build
sudo apt-get install gsl-bin
sudo apt-get install libgsl-dev
sudo apt-get install libeigen2-dev
sudo apt-get install libconfig-dev
sudo apt-get install libconfig++-dev



cmake -DNON_REALTIME:bool=true ..
sudo make

cd ~/catkin_ws/src/

catkin_create_pkg wam_common
catkin_create_pkg wam_node

cp -rf ~/Documents/Software/catkin-barrett-ros-pkg/wam_common/ .
cp -rf ~/Documents/Software/catkin-barrett-ros-pkg/wam_node/ .