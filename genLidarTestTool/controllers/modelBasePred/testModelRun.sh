#!/bin/bash


# ------------------------------------------
# Params


data=$BIN_PATH
pred=$PRED_PATH
model="cyl"


# ------------------------------------------
# Command


python modelPredTester.py -data "$data" -pred "$pred" -model "$model"


# ------------------------------------------

