#download citrix to downloads folder
cd ~/Downloads
sudo dpkg -i icaclient_13.8.0.10299729_amd64.deb
sudo apt-get install -f
sudo dpkg -i icaclient_13.8.0.10299729_amd64.deb
cd ~/Setup
sudo cp InCommonSHA2-apache.crt /opt/Citrix/ICAClient/keystore/cacerts
cd  /opt/Citrix/ICAClient/keystore/cacerts
sudo /opt/Citrix/ICAClient/util/ctx_rehash
sed -i -e 's/MouseSendsControlV=True/MouseSendsControlV=False/g' ~/.ICAClient/wfclient.ini
