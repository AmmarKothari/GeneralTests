echo "TeamViewer Install"
wget https://download.teamviewer.com/download/linux/teamviewer_amd64.deb
sudo dpkg -i teamviewer_amd64.deb
sudo apt-get -f install
sudo dpkg -i teamviewer_amd64.deb
rm teamviewer_amd64.deb
