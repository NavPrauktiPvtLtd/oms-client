#!/bin/bash

cd /home/pi/oms-client

# Fetch changes from the remote repository
git fetch

# Get the local branch's HEAD reference
local_head=$(git rev-parse HEAD)

# Compare the local HEAD with the fetched branch's HEAD
if [[ "$(git rev-parse FETCH_HEAD)" != "$local_head" ]]; then
    echo "updates available"

    if git pull; then
        sudo chmod +x ./scripts/actions.sh

        # first stop the already running application
        sudo supervisorctl stop oms_client
        # Pull was successful, proceed with the next command

        sudo pkill python

        ./scripts/actions.sh

        # Restart server
        sudo service supervisor restart
    else
        echo "Git pull failed. Unable to proceed."
    fi
else
    echo "Repository is up to date."
fi


