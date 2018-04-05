echo ""
echo ""
echo "General Packages Install"
echo ""
echo ""
sudo apt-get -y install gparted
sudo apt-get -y install pdftk
sudo apt-get -y install cmake-curses-gui
sudo apt-get -y install meshlab
sudo apt-get install -y p7zip-full
sudo apt-get install -y filezilla
sudo apt-get install -y trash-cli
sudo apt-get install -y lm-sensors


# ----- Exfat Mounting (for externals that can go between computers more easily) ---- #
sudo apt-get install -y exfat-fuse exfat-utils
