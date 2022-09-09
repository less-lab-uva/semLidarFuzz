#!/bin/bash


# -------------------------------------------------------------------------------------------------------------------

# Options

data=$BIN_PATH
labels=$LABEL_PATH
predPath=$PRED_PATH
toolData="ADD_MIRROR_ROTATE.../output/" # Edit with desired location
mongoconnect=$MONGO_CONNECT
saveAt="."


# -------------------------------------------------------------------------------------------------------------------

# Run command 

python finalVisualization.py -binPath "$data" -labelPath "$labels" -predPath "$predPath" -toolOutputPath "$toolData" -mdb "$mongoconnect" -saveAt $saveAt


# -------------------------------------------------------------------------------------------------------------------


