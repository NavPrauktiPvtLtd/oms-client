#!/bin/bash
export XAUTHORITY=/.Xauthority
export DISPLAY=:0 
export XDG_RUNTIME_DIR=$XDG_RUNTIME_DIR
python3 app/main.py
