#!/bin/bash
export XAUTHORITY=$XAUTHORITY
export DISPLAY=$DISPLAY 
export XDG_RUNTIME_DIR=$XDG_RUNTIME_DIR
python3 app/main.py
