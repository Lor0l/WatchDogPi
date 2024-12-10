#!/bin/bash

sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python3-pip -y
sudo pip install -r requirements.txt

sudo pip install opencv-contrib-python
sudo apt install -y python3-picamera2