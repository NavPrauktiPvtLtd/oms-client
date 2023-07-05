#!/bin/bash

cd "$(dirname "$0")/.."

# Fetch changes from the remote repository
git fetch

# Get the local branch's HEAD reference
local_head=$(git rev-parse HEAD)

# Compare the local HEAD with the fetched branch's HEAD
if [[ "$(git rev-parse FETCH_HEAD)" != "$local_head" ]]; then
    echo "updates available"

    sudo chmod +x actions.sh

    # first stop the already running application
    sudo supervisorctl stop oms_client

    # pull the latest repo
    git pull

    cd "$(dirname "$0")/scripts"

    ./actions.sh

    # restart server
    sudo service supervisor restart
else
    echo "Repository is up to date."
fi


