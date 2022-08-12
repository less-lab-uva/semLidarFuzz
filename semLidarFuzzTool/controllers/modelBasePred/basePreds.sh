#!/bin/bash


# ------------------------------------------


bins="/home/garrett/Documents/data/dataset/sequences/"
stage="/home/garrett/Documents/data/tmp/dataset/sequences/00/velodyne/"
pred="/home/garrett/Documents/data/resultsBase/"
# model="sq3"
# model="js3c_gpu"
# model=dar

# ------------------------------------------

# model="js3c_gpu"
# python modelBasePred.py -bins $bins -stage $stage -pred $pred -model $model

# because the model sometimes runs out of memory, keep trying
model="js3c_cpu"
until python modelBasePred.py -bins $bins -stage $stage -pred $pred -model $model
do
  echo "Trying again"
done

# ------------------------------------------


# model="ran"
# python modelBasePred.py -bins $bins -stage $stage -pred $pred -model $model



