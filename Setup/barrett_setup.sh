cd ~/Documents/Software


# This is the new method
sudo apt-get install git g++ cmake libncurses5-dev python-dev python-argparse
sudo apt-get install libeigen3-dev libboost-all-dev libgsl0-dev
sudo apt-get install libxenomai-dev libxenomai1
wget http://web.barrett.com/support/WAM_Installer/libconfig-1.4.5-PATCHED.tar.gz
tar -xf libconfig-1.4.5-PATCHED.tar.gz
cd libconfig-1.4.5
./configure && make && sudo make install
cd ../
rm -rf libconfig-1.4.5 libconfig-1.4.5-PATCHED.tar.gz

cd ~/Documents/Software
git clone https://git.barrett.com/software/libbarrett.git
cd libbarrett
cmake . -DPYTHON_INCLUDE_DIR=/usr/include/python2.7 -DPYTHON_LIBRARY=/usr/lib/x86_64-linux-gnu/libpython2.7.so
make -j8
sudo make install


# This is the older method

#sudo apt-get install gsl-bin
#sudo apt-get install libgsl-dev
#sudo apt-get install libeigen2-dev
#sudo apt-get install libconfig-dev
#sudo apt-get install libconfig++-dev
#git clone git@github.com:BarrettTechnology/libbarrett.git
#echo "git@git.barrett.com:software/libbarrett.git"
#cd libbarrett
#mkdir build
#cd build
#echo "need to modify file"
#echo "/usr/include/libconfig.h++"
#echo "search for config_setting_t"
#echo "insert the following text just above the private keyword after the second found instance"
#echo ""
#echo ""
#echo "// BARRETT(DC): Added this inline method to allow simultaneous libconfig and
#  //              libconfig++ use.
#  config_setting_t *getCSetting() const { return(_setting); }"
#echo ""
#echo ""
#read -n 1 -s -r -p "Press any key to continue when you are done"

#cmake -DNON_REALTIME:bool=true ..
#sudo make



cd ~/Documents/Software
git clone git@github.com:BenBlumer/WAMPy.git

echo "" >> ~/.bashrc
echo "#adding Barrett WAMPy Path" >> ~/.bashrc
export Barrett_WAMPy_DIR=$(pwd)
echo "export ROS_PACKAGE_PATH=$Barrett_WAMPy_DIR:\${ROS_PACKAGE_PATH}" >> ~/.bashrc

git clone git@github.com:BenBlumer/catkin-barrett-ros-pkg.git



cd ~/catkin_ws/src/

catkin_create_pkg wam_common
catkin_create_pkg wam_node

cp -rf ~/Documents/Software/catkin-barrett-ros-pkg/wam_common/ .
cp -rf ~/Documents/Software/catkin-barrett-ros-pkg/wam_node/ .
