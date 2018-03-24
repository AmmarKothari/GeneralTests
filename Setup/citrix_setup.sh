#download citrix to downloads folder
curdir=$(cd `dirname $0` && pwd)
echo "Download the pacakge. Hit enter once it is downloaded."
xdg-open https://www.citrix.com/downloads/citrix-receiver/linux/receiver-for-linux-latest.html
read -n 1 -s
cd ~/Downloads
sudo dpkg -i icaclient_*
sudo apt-get -y install -f
sudo dpkg -i icaclient_*
cd $curdir
sudo cp InCommonSHA2-apache.crt /opt/Citrix/ICAClient/keystore/cacerts
cd  /opt/Citrix/ICAClient/keystore/cacerts
sudo /opt/Citrix/ICAClient/util/ctx_rehash
echo "Start Citrix"
echo "change to window opening"
echo "map drive"
echo "Hit enter when you are done"
read -n 1 -s
sed -i -e 's/MouseSendsControlV=True/MouseSendsControlV=False/g' ~/.ICAClient/wfclient.ini
