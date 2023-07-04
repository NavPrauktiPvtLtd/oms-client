#!/bin/bash

# Error out if anything fails.
set -e


# Make sure script is run as root.
if [ "$(id -u)" != "0" ]; then
  echo "Must be run as root with sudo! Try: sudo ./install.sh"
  exit 1
fi

read -p "Enter SERIAL_NO: " SERIAL_NO

read -p "Enter MAX_VIDEO_STORAGE_SIZE [default: 20000000000]: " MAX_VIDEO_STORAGE_SIZE
MAX_VIDEO_STORAGE_SIZE=${MAX_VIDEO_STORAGE_SIZE:-20000000000}  # Set default value if empty

read -p "Enter MQTT_HOST: " MQTT_HOST

read -p "Enter DISPLAY [default: :0]: " DISPLAY
DISPLAY=${DISPLAY:-:0}  # Set default value if empty

read -p "Enter DEVICE_TYPE (1- linux, 2 - pi) [default: 1]: " DEVICE_TYPE
DEVICE_TYPE=${DEVICE_TYPE:-:1}  
                                                                                                                                                                                                                                                      
read -p "Enter update interval[2-59]: [default: 1 min] " INTERVAL
INTERVAL=${INTERVAL:-:1}

# Validate the user input
if [[ ! $INTERVAL =~ ^[0-9]+$ ]]; then
  echo "Invalid input. Please enter a positive integer value."
  exit 1
fi

cat << EOF > .env
SERIAL_NO=$SERIAL_NO
MAX_VIDEO_STORAGE_SIZE=$MAX_VIDEO_STORAGE_SIZE
MQTT_HOST=$MQTT_HOST
DISPLAY=$DISPLAY
DEVICE_TYPE=$DEVICE_TYPE
EOF

echo "Environment file generated successfully!"

echo "Updating the device"

sudo apt-get update -y
sudo apt-get dist-upgrade -y

echo "Installing required packages"

dpkg -s vlc 2>/dev/null >/dev/null || sudo apt install vlc -y

dpkg -s python3 2>/dev/null >/dev/null || sudo apt install python3 -y

dpkg -s python3-pip 2>/dev/null >/dev/null || sudo apt install python3-pip -y

dpkg -s supervisor 2>/dev/null >/dev/null || sudo apt install supervisor -y

mkdir videos

pip3 install -r requirements.txt

sudo chmod +x run.sh

sudo chmod +x update.sh

#Create supervisor conf file

echo "Creating supervisor config file"
echo "==========================================="

cat <<EOF >oms-client.conf
[program:oms_client]
command=$('pwd')/run.sh
directory=$('pwd')
user=pi
autostart=true
autorestart=true
stderr_logfile=/var/log/oms.err.log
stdout_logfile=/var/log/oms.out.log
EOF

cp -f oms-client.conf /etc/supervisor/conf.d/

service supervisor restart

# get the current dir path
current_dir=$(dirname "$(readlink -f "$0")")

chmod +x "${current_dir}/update.sh"

(crontab -l ; echo "*/$minutes * * * * ${current_dir}/update.sh") | crontab -

echo "Finished!"