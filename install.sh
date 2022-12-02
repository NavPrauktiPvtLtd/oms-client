#!/bin/bash

# Error out if anything fails.
set -e


# Make sure script is run as root.
if [ "$(id -u)" != "0" ]; then
  echo "Must be run as root with sudo! Try: sudo ./install.sh"
  exit 1
fi


sudo apt-get update -y
sudo apt-get dist-upgrade -y

sudo apt install firefox-esr -y

dpkg -s vlc 2>/dev/null >/dev/null || sudo apt install vlc -y

dpkg -s python3 2>/dev/null >/dev/null || sudo apt install python3 -y

dpkg -s python3-pip 2>/dev/null >/dev/null || sudo apt install python3-pip -y

dpkg -s supervisor 2>/dev/null >/dev/null || sudo apt install supervisor -y

sudo apt install python3-venv -y

pip3 install virtualenv

python3 -m venv venv
. ./venv/bin/activate
pip3 install -r requirements.txt

sudo chmod +x run.sh


#Create supervisor conf file

echo "Creating supervisor config file"
echo "==========================================="

cat <<EOF >oms-client.conf
[program:oms_client]
command=$('pwd')/run.sh
directory=$('pwd')
user=$('whoami')
autostart=true
autorestart=true
stderr_logfile=/var/log/oms.err.log
stdout_logfile=/var/log/oms.out.log
EOF

cp oms-client.conf /etc/supervisor/conf.d/

service supervisor restart

echo "Finished!"