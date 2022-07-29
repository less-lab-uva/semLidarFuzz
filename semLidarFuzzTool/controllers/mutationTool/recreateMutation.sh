#!/bin/bash


# ------------------------------------------


# Original scans
binPath="/home/garrett/Documents/data/dataset/sequences/"
# Labels for those scans
lblPath="/home/garrett/Documents/data/dataset4/sequences/"
# Models original predictions on those scans
predPath="/home/garrett/Documents/data/resultsBase/"
# Full path to the mongo connect
mongoconnect="/home/garrett/Documents/lidarTest2/mongoconnect.txt"
# Path to model directory
modelDir="/home/garrett/Documents"

# Models to use for the run comma seperated
models="cyl,spv,sal,sq3,pol"
# Total count of total mutations to generate 
count=30
# How often evaluation will trigger
batch=15


# Use one of these
mutationId="Vp4eqHDihWWypjswh3gnVU-VEHICLE_SCALE"
batchId="Vz6d37G4oKABGMXSpheek9"


# ------------------------------------------


python semFuzzLidar.py -redoBatchId $batchId -binPath "$binPath" -labelPath $lblPath -predPath $predPath -mdb $mongoconnect -modelDir $modelDir -mutation $mutation -count $count -batch $batch -saveAt $newSaveDir -models $models
# python semFuzzLidar.py -redoMutationId $mutationId -binPath "$binPath" -labelPath $lblPath -predPath $predPath -mdb $mongoconnect -modelDir $modelDir -mutation $mutation -count $count -batch $batch -saveAt $newSaveDir -models $models


# ------------------------------------------



