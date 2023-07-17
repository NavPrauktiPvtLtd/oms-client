#!/bin/bash
export XAUTHORITY=/home/pi/.Xauthority
export DISPLAY=:0 
export XDG_RUNTIME_DIR=$XDG_RUNTIME_DIR
sudo chmod +x update.sh
sudo ./update.sh
sudo python3 app/main.py
