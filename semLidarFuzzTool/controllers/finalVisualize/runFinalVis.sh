#!/bin/bash


# -------------------------------------------------------------------------------------------------------------------

# Options

data="/home/garrett/Documents/data/dataset/sequences"
labels="/home/garrett/Documents/data/dataset4/sequences"
predPath="/home/garrett/Documents/data/resultsBase"
# toolData="/home/garrett/Documents/lidarTest2/toolV5/output/"
# toolData="/media/garrett/ExtraDrive1/output/"
toolData="/media/garrett/ExtraDrive1/2kwed/ADD_MIRROR_ROTATE_2022_07_25-18_48_35/output/"
mongoconnect="/home/garrett/Documents/lidarTest2/mongoconnect.txt"
# saveAt="/home/garrett/Documents/lidarTest2/toolV5/output"
saveAt="/media/garrett/ExtraDrive1/output"


# -------------------------------------------------------------------------------------------------------------------

# Run command 

python finalVisualization.py -binPath "$data" -labelPath "$labels" -predPath "$predPath" -toolOutputPath "$toolData" -mdb "$mongoconnect" -saveAt $saveAt


# -------------------------------------------------------------------------------------------------------------------


