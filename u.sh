#!/bin/bash

# Fetch changes from the remote repository
git fetch

# Get the local branch's HEAD reference
local_head=$(git rev-parse HEAD)

# Compare the local HEAD with the fetched branch's HEAD
if [[ "$(git rev-parse FETCH_HEAD)" != "$local_head" ]]; then
    echo "Repository has been updated."
else
    echo "Repository is up to date."
fi