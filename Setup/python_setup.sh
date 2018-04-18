
#-- Python Packages -- #
sudo apt-get install -y python3-pip ipython3
pip3 install --upgrade pip
pip3 install pdbpp matplotlib

echo " "
echo "#Python Path" >> ~/.bashrc
echo "export PYTHONPATH=/home/ammar/Documents/Projects:${PYTHONPATH}" >> ~/.bashrc

# -- Set Python3 as Default --#
echo "#Setting Default to Python 3" >> ~/.bashrc
echo "alias python=python3" >> ~/.bashrc

# -- Install python things --#
sudo apt-get install -y ipython python-pip
sudo apt-get install -y python-tk
sudo apt-get install -y matplotlib
sudo apt-get install -y Pillow
sudo apt-get install -y python-seaborn python3-seaborn
sudo apt-get install -y python-setuptools
sudo pip install pdbpp
sudo pip install --upgrade pip
sudo apt-get install -y python-pip3
sudo pip install progressbar
sudo pip install scikit-learn
sudo pip install Cython


# setting up ipython
ipython profile create
sudo cp -f ipython_config.py ~/.ipython/profile_default

