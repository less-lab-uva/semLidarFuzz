#!/bin/bash

# Allows the tool import other files


# ------------------------------------------------------------------------

echo 
echo "Running Environment Setup"
echo 

# ------------------------------------------------------------------------

# Python Path, should be the root of the tool (where this script is)
toolPath=$(pwd)
echo "Setting PYTHONPATH to $toolPath"
export PYTHONPATH=${PYTHONPATH}:$(pwd)
echo $PYTHONPATH
echo 

# ------------------------------------------------------------------------



