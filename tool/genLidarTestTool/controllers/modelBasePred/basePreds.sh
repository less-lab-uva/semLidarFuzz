#!/bin/bash


# ------------------------------------------


bins=$BIN_PATH
stage=$STAGE_PATH
pred=$PRED_PATH

for model in  "cyl" "spv" "js3c_gpu" "sal" "sq3"
do
  until python modelBasePred.py -bins $bins -stage $stage -pred $pred -model $model
  do
    echo "Trying again"
  done

done

# ------------------------------------------




