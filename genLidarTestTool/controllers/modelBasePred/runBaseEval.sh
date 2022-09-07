#!/bin/bash


# ------------------------------------------


labelBasePath=$LABEL_PATH
predBasePath=$PRED_PATH


# ------------------------------------------


python modelEvaluationInitial.py -labels $labelBasePath -pred $predBasePath


# ------------------------------------------



