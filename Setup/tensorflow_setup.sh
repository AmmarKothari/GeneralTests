# sudo apt-get install python-pip python-dev
# sudo pip install tensorflow-gpu

MAIN_DIR='/usr/local/cuda-9.1/lib64'

sudo ln -s $MAIN_DIR/libcublas.so.9.1 $MAIN_DIR/libcublas.so.9.0 || 
sudo ln -s $MAIN_DIR/libcusolver.so.9.1 $MAIN_DIR/libcusolver.so.9.0 ||
sudo ln -s $MAIN_DIR/libcudart.so.9.1 $MAIN_DIR/libcudart.so.9.0
sudo ln -s $MAIN_DIR/libcudnn.so.9.1 $MAIN_DIR/libcudnn.so.9.0
