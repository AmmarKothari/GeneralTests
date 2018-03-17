# ---- Install Chrome ---- #
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt-get install libindicator7 libappindicator1
sudo dpkg -i google-chrome*.deb
rm google-chrome-stable_current_amd64.deb
log_all "Chrome Installed"