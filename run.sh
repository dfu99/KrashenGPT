#!/usr/bin/env bash

# Get the current directory
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
echo $SCRIPT_DIR

# Check if instance directory exists
if [ ! -d "$SCRIPT_DIR"/instance ]; then
	mkdir instance
fi

# Simple bootup, start redis-server in the background
redis-server&
python krashen-flask.py
