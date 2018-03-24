ssh-keygen -t rsa -b 4096 -C "amarsbars@gmail.com" -f ~/.ssh/id_rsa -N ''
ssh-add ~/.ssh/id_rsa
sudo apt-get -y install xclip
xclip -sel clip < ~/.ssh/id_rsa.pub
echo "https://help.github.com/articles/adding-a-new-ssh-key-to-your-github-account/"
xdg-open https://help.github.com/articles/adding-a-new-ssh-key-to-your-github-account/
echo -ne '\n'
xdg-open https://github.com/settings/ssh/new
echo -ne '\n'
echo "When done adding to account, hit enter, to start downloading repos"
read -n 1 -s
cd ~/Documents/Projects
git clone git@github.com:amarsbars/CE661_KinPosNav.git
git clone git@github.com:amarsbars/GeneralTests.git
git clone git@github.com:amarsbars/ROB541_GeometricMecahnics.git
git clone git@github.com:amarsbars/ControlsLearning.git
git clone git@github.com:OSUrobotics/NearContactStudy.git

