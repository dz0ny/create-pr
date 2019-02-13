#!/bin/bash

set -e

# Ensure that the file path is present
if [[ -z "$1" ]]; then
  echo "You must pass at least one argument to this action, the path to the patching recepie."
  exit 1
fi
echo "Appending patch file $1 to main"
cat $1 >> /main.py
echo "Run patch file in main"
python /main.py
