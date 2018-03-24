cd ..
sudo apt-get -y purge nvidia*
sudo add-apt-repository -y ppa:graphics-drivers
sudo apt-get -y update
cd Setup
sudo apt-get install nvidia-390
