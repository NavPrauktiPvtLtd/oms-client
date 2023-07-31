#!/bin/bash

# Check if NetworkManager is installed
if ! command -v nmcli &>/dev/null; then
  echo "NetworkManager (nmcli) is not installed. Please install NetworkManager before running this script."
  exit 1
fi

# Check if the WiFi device is available
wifi_device=$(nmcli device status | grep wifi | awk '{print $1}')
if [ -z "$wifi_device" ]; then
  echo "WiFi device not found. Make sure your WiFi adapter is available and enabled."
  exit 1
fi


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


# Check if already connected to the WiFi network
if nmcli connection show --active | grep -q "$wifi_ssid"; then
  echo "Already connected to $wifi_ssid."
  exit 0
fi


# Turn on the WiFi device
sudo nmcli radio wifi on

# Wait for a moment to enable the WiFi radio
sleep 2

# Connect to the WiFi network
sudo nmcli device wifi connect "$wifi_ssid" password "$wifi_password"

# # Check the connection status
# if nmcli device status | grep "$wifi_ssid" | grep -q "connected"; then
#   echo "Connected to $wifi_ssid successfully."
# else
#   echo "Connection to $wifi_ssid failed."
# fi
