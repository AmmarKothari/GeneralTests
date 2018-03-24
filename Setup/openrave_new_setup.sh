cd ~/Documents/Software
git clone https://github.com/crigroup/openrave-installation.git
cd openrave-installation
./install-dependencies.sh
sudo apt-get install -y libgstreamer1.0-0 gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-doc gstreamer1.0-tools
sudo apt-get install -y libgdal1i libgdal1-dev libgl1-mesa-glx libsdl2-2.0-0 libsdl2-dev
sudo apt-get install -y libsdl-image1.2-dev libsdl-dev
sudo apt-get install python-poppler
sudo rm /usr/lib/x86_64-linux-gnu/libGL.so
sudo ln -s /usr/lib/libGL.so.1 /usr/lib/x86_64-linux-gnu/libGL.so
sudo ./install-osg.sh
sudo make install_ld_conf
sudo chown $USER:$USER -R ~/git
sudo ./install-fcl.sh
sudo ./install-openrave.sh
