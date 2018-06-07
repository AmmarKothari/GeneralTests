wget -qO - https://download.sublimetext.com/sublimehq-pub.gpg | sudo apt-key add -
sudo apt-get install -y apt-transport-https
echo "deb https://download.sublimetext.com/ apt/stable/" | sudo tee /etc/apt/sources.list.d/sublime-text.list
sudo apt-get update
sudo apt-get install sublime-text

echo "Install Package Control"
wget https://packagecontrol.io/Package%20Control.sublime-package
mv Package\ Control.sublime-package ~/.config/sublime-text-3/Installed\ Packages/


echo "Install Latex Packages"
sudo apt-get install -y texlive-latex-recommended texlive-latex-extra biber texlive-bibtex-extra latexmk

# copy config file to directory -- should install all packages automatically
cp Package\ Control.sublime-settings ~/.config/sublime-text-3/Installed Packages
