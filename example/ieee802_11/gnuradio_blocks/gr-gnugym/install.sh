#!/bin/sh

mkdir build
cd build
cmake ../
make
sudo make install
sudo ldconfig
