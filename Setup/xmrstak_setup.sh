sudo apt-get install -y libmicrohttpd-dev libssl-dev cmake build-essential libhwloc-dev
cd ~/Documents/Software
git clone git@github.com:fireice-uk/xmr-stak.git
cd xmr-stak
#sed -i 'constexpr double fDevDonationLevel = * \/ 100.0/c\ constexpr double fDevDonationLevel = 0.0 \/ 100.0' xmrstak/donate-level.hpp
mkdir build
cd build
cmake .. -DCUDA_ENABLE=OFF -DOpenCL_ENABLE=OFF
sudo make
sudo make install

sudo sysctl -w vm.nr_hugepages=128
sudo cp -f limits.conf /etc/security
