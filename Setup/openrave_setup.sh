

###########################################################
#
# OpenRAVE
# https://scaron.info/teaching/installing-openrave-on-ubuntu-16.04.html
###########################################################
log_all "Starting OpenRAVE Install"
cd ~/Documents/SoftwareSource
sudo apt-get -y install cmake g++ git ipython minizip python-dev python-h5py python-numpy python-scipy python-sympy qt4-dev-tools

sudo apt-get -y install libassimp-dev libavcodec-dev libavformat-dev libavformat-dev libboost-all-dev libboost-date-time-dev libbullet-dev libfaac-dev libglew-dev libgsm1-dev liblapack-dev liblog4cxx-dev libmpfr-dev libode-dev libogg-dev libpcrecpp0v5 libpcre3-dev libqhull-dev libqt4-dev libsoqt-dev-common libsoqt4-dev libswscale-dev libswscale-dev libvorbis-dev libx264-dev libxml2-dev libxvidcore-dev

#Collada
cd ~/Documents/SoftwareSource
git clone https://github.com/rdiankov/collada-dom.git
cd collada-dom && mkdir build && cd build
cmake ..
make -j4
sudo make install
log_all "    Collada Installed"

#Open Scene Graph
cd ~/Documents/SoftwareSource
sudo apt-get -y install libcairo2-dev libjasper-dev libpoppler-glib-dev libsdl2-dev libtiff5-dev libxrandr-dev
git clone --branch OpenSceneGraph-3.4 https://github.com/openscenegraph/OpenSceneGraph.git
cd OpenSceneGraph && mkdir build && cd build
cmake .. -DDESIRED_QT_VERSION=4
make -j `nproc`
sudo make install
sudo make install_ld_conf
log_all "    OpenSceneGraph Installed"

#fcl
cd ~/Documents/SoftwareSource/
sudo apt-get -y install libccd-dev
git clone https://github.com/flexible-collision-library/fcl.git
cd fcl
git checkout 0.5.0  # use FCL 0.5.0
mkdir build && cd build
cmake ..
make -j `nproc`
sudo make install

cd ~/Documents/SoftwareSource
git clone https://github.com/flexible-collision-library/fcl
cd fcl; git reset --hard 0.5.0
cd build
cmake ..
make -j `nproc`
sudo make install
sudo ln -sf /usr/include/eigen3/Eigen /usr/include/Eigen
log_all "    FCL Installed"

cd ~/Documents/SoftwareSource
git clone --branch latest_stable https://github.com/rdiankov/openrave.git
cd openrave && mkdir build && cd build
cmake .. -DOSG_DIR=/usr/local/lib64/
make -j `nproc`
sudo make install
echo “#OpenRave variables” >> ~/.bashrc
echo "LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$(openrave-config --python-dir)/openravepy/_openravepy_" >> ~/.bashrc
echo “LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$(openrave-config --python-dir)/openravepy/_openravepy_”  >> ~/.bashrc
export PYTHONPATH=$PYTHONPATH:$(openrave-config --python-dir)
log_all "    OpenRAVE Downloaded and Installed"
