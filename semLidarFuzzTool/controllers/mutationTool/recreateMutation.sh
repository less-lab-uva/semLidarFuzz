#!/bin/bash


# ------------------------------------------


# Original scans
binPath=$BIN_PATH
# Labels for those scans
lblPath=$LABEL_PATH
# Models original predictions on those scans
predPath=$PRED_PATH
# Full path to the mongo connect
mongoconnect=$MONGO_CONNECT
# Path to model directory
modelDir=$MODEL_DIR

# Models to use for the run comma seperated
models=$MODELS
# Total count of total mutations to generate 
count=30
# How often evaluation will trigger
batch=15


# TODO Replace with desired
mutationId="Vp4eqHDihWWypjswh3gnVU-VEHICLE_SCALE"
batchId="Vz6d37G4oKABGMXSpheek9"


# ------------------------------------------


python semFuzzLidar.py -redoBatchId $batchId -binPath "$binPath" -labelPath $lblPath -predPath $predPath -mdb $mongoconnect -modelDir $modelDir -mutation $mutation -count $count -batch $batch -saveAt $newSaveDir -models $models


# ------------------------------------------



