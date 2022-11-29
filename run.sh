#!/bin/bash
export XAUTHORITY=$XAUTHORITY
export DISPLAY=$DISPLAY 
export XDG_RUNTIME_DIR=$XDG_RUNTIME_DIR
. ./venv/bin/activate
python3 main.py
