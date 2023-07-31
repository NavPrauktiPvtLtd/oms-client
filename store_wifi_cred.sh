#!/bin/bash

# Check if two arguments are provided
if [ $# -ne 2 ]; then
  echo "Usage: $0 <string1> <string2>"
  exit 1
fi

# Get the two arguments
ssid="$1"
password="$2"

sudo echo $ssid > new.txt
sudo echo $password >> new.txt
