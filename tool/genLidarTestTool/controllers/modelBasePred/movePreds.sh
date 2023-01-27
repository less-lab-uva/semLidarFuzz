#!/bin/bash


# ------------------------------------------
# Helper depending on where the model saves the results


# ------------------------------------------

for model in "sq3" "sal"
do
    for folder in "00" "01" "02" "03" "04" "05" "06" "07" "08" "09" "10"
    do
        mv $PRED_PATH/$folder/$model/sequences/00/predictions/*.label $PRED_PATH$folder/$model
        rm -rf $PRED_PATH$folder/$model/sequences
    done
done



