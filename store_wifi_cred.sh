#!/bin/bash

# Check if two arguments are provided
if [ $# -ne 2 ]; then
  echo "Usage: $0 <string1> <string2>"
  exit 1
fi

# Get the two arguments
ssid="$1"
password="$2"

sudo echo $ssid > /home/pi/oms-client/wifi_credentials.txt
sudo echo $password >> /home/pi/oms-client/wifi_credentials.txt
