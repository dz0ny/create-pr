#!/bin/bash

set -e

# Ensure that the GITHUB_TOKEN secret is included
if [[ -z "$GITHUB_TOKEN" ]]; then
  echo "Set the GITHUB_TOKEN env variable."
  exit 1
fi

# Ensure that the file path is present
if [[ -z "$1" ]]; then
  echo "You must pass at least one argument to this action, the path to the patching recepie."
  exit 1
fi
echo "Appending patch file $1 to main"
cat $1 >> /main.py
echo "Run patch file in main"
python /main.py
