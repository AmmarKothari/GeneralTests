echo "Instructions: https://github.com/IntelRealSense/librealsense/blob/v1.12.1/doc/installation.md"
sudo apt-get install libusb-1.0-0-dev pkg-config
sudo apt-get install libglfw3-dev
sudo apt-get install libgtk-3-dev
cd ~/Documents/Software
git clone git@github.com:IntelRealSense/librealsense.git
cd librealsense
cmake .. -DBUILD_EXAMPLES:BOOL=true
make -j8
sudo make install
#sudo cp config/99-realsense-libusb.rules /etc/udev/rules.d/
#sudo udevadm control --reload-rules && udevadm trigger
#./scripts/patch-uvcvideo-16.04.simple.sh
#sudo modprobe uvcvideo
#sudo dmesg | tail -n 50


sudo apt-get install ros-kinetic-realsense-camera
