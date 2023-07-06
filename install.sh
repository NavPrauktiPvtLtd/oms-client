#!/bin/bash

# Error out if anything fails.
set -e

# Make sure script is run as root.
if [ "$(id -u)" != "0" ]; then
  echo "Must be run as root with sudo! Try: sudo ./install.sh"
  exit 1
fi

chmod +x "./scripts/actions.sh"

chmod +x "./scripts/delete-log.sh"

chmod +x "./scripts/restart.sh"

chmod +x "./scripts/uninstall.sh"

chmod +x "./scripts/stop.sh"

read -p "Enter SERIAL_NO: " SERIAL_NO

read -p "Enter MAX_VIDEO_STORAGE_SIZE [default: 20000000000]: " MAX_VIDEO_STORAGE_SIZE
MAX_VIDEO_STORAGE_SIZE=${MAX_VIDEO_STORAGE_SIZE:-20000000000}  # Set default value if empty

read -p "Enter MQTT_HOST: " MQTT_HOST

read -p "Enter MQTT username: " MQTT_USERNAME

read -p "Enter MQTT password: " MQTT_PASSWORD

read -p "Enter DISPLAY [default: :0]: " DISPLAY
DISPLAY=${DISPLAY:-:0}  # Set default value if empty

read -p "Enter DEVICE_TYPE (1- linux, 2 - pi) [default: 1]: " DEVICE_TYPE
DEVICE_TYPE=${DEVICE_TYPE:-:1}  
                                                                                                                                                                                                                                                      
echo "Environment file generated successfully!"

echo "Updating the device"

sudo apt-get update -y

sudo apt-get dist-upgrade -y

echo "Installing required packages"

dpkg -s vlc 2>/dev/null >/dev/null || sudo apt install vlc -y

dpkg -s python3 2>/dev/null >/dev/null || sudo apt install python3 -y

dpkg -s python3-pip 2>/dev/null >/dev/null || sudo apt install python3-pip -y

dpkg -s supervisor 2>/dev/null >/dev/null || sudo apt install supervisor -y

#Create supervisor conf file

echo "Creating supervisor config file"

echo "==========================================="

cat <<EOF >oms_client.conf
[program:oms_client]
command=$('pwd')/run.sh
directory=$('pwd')
user=pi
autostart=true
autorestart=true
stderr_logfile=/home/pi/oms-client/logs/err.log
stdout_logfile=/home/pi/oms-client/logs/out.log
EOF

cp -f oms_client.conf /etc/supervisor/conf.d/

cat << EOF > .env
SERIAL_NO=$SERIAL_NO
MAX_VIDEO_STORAGE_SIZE=$MAX_VIDEO_STORAGE_SIZE
MQTT_HOST=$MQTT_HOST
MQTT_USERNAME=$MQTT_USERNAME
MQTT_PASSWORD=$MQTT_PASSWORD
DISPLAY=$DISPLAY
DEVICE_TYPE=$DEVICE_TYPE
EOF

if [ ! -d "videos" ]; then
    mkdir videos
fi

if [ ! -f "videos/playback_history.json" ]; then
    touch videos/playback_history.json
fi

if [ ! -d "logs" ]; then
    mkdir logs
fi

dir=$('pwd')

pip3 install -r ${dir}/requirements.txt

sudo pkill python

service supervisor restart

echo "Finished!"