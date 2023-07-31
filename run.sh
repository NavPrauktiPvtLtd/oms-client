#!/bin/bash
export XAUTHORITY=/home/pi/.Xauthority
export DISPLAY=:0 
export XDG_RUNTIME_DIR=$XDG_RUNTIME_DIR


if [ ! -f /home/pi/oms-client/wifi_credentials.txt ]; then
echo "WiFi credential file 'wifi_credential.txt' not found."
exit 1
fi

readarray -t credentials < /home/pi/oms-client/wifi_credentials.txt
if [ ${#credentials[@]} -lt 2 ]; then
echo "Invalid credential file format. It should contain SSID and password on separate lines."
exit 1
fi

wifi_ssid="${credentials[0]}"
wifi_password="${credentials[1]}"

# check if wifi is connected

sudo chmod +x /home/pi/oms-client/wifi-connector.sh



# Loop to run the "connect_wifi.sh" script until Wi-Fi is connected
while true; do
    
    # Check the connection status
    if nmcli device status | grep "$wifi_ssid" | grep -q "connected"; then
    echo "Connected to $wifi_ssid successfully."
    break;
    else
    echo "Trying t coonnect...."
    sudo /home/pi/oms-client/wifi-connector.sh
    sleep 10
    fi

done

# Get the local branch's HEAD reference
local_head=$(git rev-parse HEAD)

# Compare the local HEAD with the fetched branch's HEAD
if [[ "$(git rev-parse FETCH_HEAD)" != "$local_head" ]]; then
    echo "updates available"

    if git pull; then
        sudo chmod +x /home/pi/oms-client/scripts/actions.sh

        # first stop the already running application
        sudo supervisorctl stop oms_client
        # Pull was successful, proceed with the next command

        sudo pkill python

        sudo /home/pi/oms-client/scripts/actions.sh

        # Restart server
        sudo service supervisor restart
    else
        echo "Git pull failed. Unable to proceed."
    fi
else
    echo "No updates found"
    echo "Running app...."
    sudo python3 app/main.py
fi
