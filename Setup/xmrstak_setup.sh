sudo apt-get install -y libmicrohttpd-dev libssl-dev cmake build-essential libhwloc-dev
cd ~/Documents/Software
git clone git@github.com:fireice-uk/xmr-stak.git
cd xmr-stak
mkdir build
cd build
cmake .. -DCUDA_ENABLE=OFF -DOpenCL_ENABLE=OFF
sudo make
sudo make install