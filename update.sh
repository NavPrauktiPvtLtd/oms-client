#!/bin/bash

output=$(git fetch -v --dry-run | grep "\[up-to-date\]")
echo $output

if [ -z "$output"=="" ]; then
    echo "no updates available"
else
    echo "updates available"

    sudo chmod +x actions.sh

    # first stop the already running application
    sudo supervisorctl stop oms_client

    # pull the latest repo
    git pull

    ./actions.sh

    # restart server
    service supervisor restart 
fi