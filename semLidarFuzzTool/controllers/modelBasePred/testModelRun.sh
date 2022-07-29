#!/bin/bash


# ------------------------------------------
# Params


data="/home/garrett/Documents/data/tmp/dataset"
pred="/home/garrett/Documents/data/out"
model="cyl"
model="spv"
model="sal"
model="sq3"
model="pol"
# model="ran"


# ------------------------------------------
# Command


python modelPredTester.py -data "$data" -pred "$pred" -model "$model"


# ------------------------------------------

