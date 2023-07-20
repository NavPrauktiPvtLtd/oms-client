#!/bin/bash
export XAUTHORITY=/home/pi/.Xauthority
export DISPLAY=:0 
export XDG_RUNTIME_DIR=$XDG_RUNTIME_DIR



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