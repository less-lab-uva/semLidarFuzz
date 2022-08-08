#!/bin/bash


# ------------------------------------------


bins="/home/garrett/Documents/data/dataset/sequences/"
stage="/home/garrett/Documents/data/tmp/dataset/sequences/00/velodyne/"
pred="/home/garrett/Documents/data/resultsBase/"
# model="sq3"
model="js3c_gpu"
# model=dar

# ------------------------------------------

model="js3c_gpu"
python modelBasePred.py -bins $bins -stage $stage -pred $pred -model $model
model="js3c_cpu"
python modelBasePred.py -bins $bins -stage $stage -pred $pred -model $model


# ------------------------------------------


#model="ran"
#python modelBasePred.py -bins $bins -stage $stage -pred $pred -model $model



