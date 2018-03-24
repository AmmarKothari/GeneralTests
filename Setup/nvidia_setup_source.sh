sudo cp -f blacklist.conf /etc/modprobe.d/blacklist.conf
sudo apt-get remove --purge nvidia-*
sudo update-initramfs -u

cd ~/Downloads
wget http://us.download.nvidia.com/XFree86/Linux-x86_64/390.42/NVIDIA-Linux-x86_64-390.42.run
chmod +x NVIDIA-Linux-x86_64-390.42.run
echo "Reboot now (sudo reboot)"
echo "Switch to terminal and stop lightdm"
echo "sudo bash NVIDIA-Linux-x86_64-390.42.run"
