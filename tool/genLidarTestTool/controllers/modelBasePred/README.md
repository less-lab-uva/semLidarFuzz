# Model Base Prediction

Scripts to perform the preprocessing step of collecting base predicitons

---

## Model Base Predictions

- modelBasePred.py
- Obtains the valid instances to use in mutation
- Note if the model produces results as /sequences/00/predictions/ movePreds.sh can be used to be used to realign them 

### Arguments
| Argument | Usage |
| ----- | ------------ |
| ```-bins PATH``` | Path to the scan bin files, expected to be given in the format of /path/dataset/sequences/ |
| ```-stage PATH``` | Path to a stage directory .../dataset/sequences/00/velodyne/ |
| ```-pred PATH``` | Path to the location to save the model predictions to |
| ```-model MODEL``` | model to get the predictions for |


---

## Model Evaluation Initial

- modelEvaluationInitial.py
- Runs through 
- Was used to validate the accuracy and jaccard were as expected and when the flow did not involve creating modified predictions

---

## Model Prediction Tester

- modelPredictionTester.py
- Can be run to test a folder of predictions
- Used to evaluate the docker runners were functioning correctly

---



