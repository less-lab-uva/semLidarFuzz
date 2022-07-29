#!/bin/bash


# ------------------------------------------


bins="/home/garrett/Documents/data/dataset/sequences/"
stage="/home/garrett/Documents/data/tmp/dataset/sequences/00/velodyne/"
pred="/home/garrett/Documents/data/resultsBase/"
# model="sq3"
model="pol"
# model=dar

# ------------------------------------------


python modelBasePred.py -bins $bins -stage $stage -pred $pred -model $model


# ------------------------------------------


model="ran"
python modelBasePred.py -bins $bins -stage $stage -pred $pred -model $model



