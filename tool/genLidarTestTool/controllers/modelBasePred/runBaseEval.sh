#!/bin/bash


# ------------------------------------------


labelBasePath=$LABEL_PATH
predBasePath=$PRED_PATH


# ------------------------------------------

for model in ${MODELS//,/ }
do
  python3 modelBasePred.py -bins $BIN_PATH -pred $predBasePath -model $model -modelDir $MODEL_DIR -stage $STAGING_DIR
done
source movePreds.sh
python3 modelEvaluationInitial.py -labels $labelBasePath -pred $predBasePath -models $MODELS


# ------------------------------------------



