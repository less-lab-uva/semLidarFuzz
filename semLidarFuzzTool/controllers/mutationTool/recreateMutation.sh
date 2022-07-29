#!/bin/bash


# ------------------------------------------


binPath="/home/garrett/Documents/data/dataset/sequences/"
lblPath="/home/garrett/Documents/data/dataset2/sequences/"
mongoconnect="/home/garrett/Documents/lidarTest2/mongoconnect.txt"
saveAt="/home/garrett/Documents/lidarTest2/toolV5/controllers/mutationTool"

# Use one of these
mutationId="GnZmgeWHocGTvYaR9Un5Ed-ADD_ROTATE"
batchId="Jniz6rmaXE4bPeFu6hXDFR"


# ------------------------------------------


python redoMutation.py -binPath "$binPath" -labelPath $lblPath -mdb $mongoconnect -saveAt $saveAt -mutationId $mutationId
# python redoMutation.py -binPath "$binPath" -labelPath $lblPath -mdb $mongoconnect -saveAt $saveAt -batchId $batchId


# ------------------------------------------



