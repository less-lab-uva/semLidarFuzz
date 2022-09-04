#!/bin/bash

# Allows the tool import other files


# ------------------------------------------------------------------------

echo 
echo "Running Environment Setup"
echo 


# TODO EDIT
# Directory to save results in
export SAVE_DIR=""
# Full path to the mongo connect
export MONGO_CONNECT=""
# Original scans
export BIN_PATH=""
# Labels for those scans
export LABEL_PATH=""
# Models original predictions on those scans
export PRED_PATH=""
# Path to location of models
export MODEL_DIR=""
# Path on disk that can be used for temporary files
export STAGE_DIR="/tmp"
export MODELS="cyl,spv,js3c_gpu,sal,sq3"
# ------------------------------------------------------------------------

# Python Path, should be the root of the tool (where this script is)
toolPath=$(pwd)
echo "Setting PYTHONPATH to $toolPath"
export PYTHONPATH=${PYTHONPATH}:$(pwd)
echo $PYTHONPATH
echo
# ------------------------------------------------------------------------



