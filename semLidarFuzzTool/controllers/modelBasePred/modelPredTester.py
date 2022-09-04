"""
modelPredTester
Script to help test the models

@Date 7/22/22
"""


import argparse

from domain.modelConstants import Models

from service.models.cylRunner import CylRunner
from service.models.js3cCPURunner import JS3CCPURunner
from service.models.js3cGPURunner import JS3CGPURunner
from service.models.spvRunner import SpvRunner
from service.models.salRunner import SalRunner
from service.models.sq3Runner import Sq3Runner
from service.models.polRunner import PolRunner
from service.models.ranRunner import RanRunner


# -------------------------------------------------------------


def parse_args():
    p = argparse.ArgumentParser(
        description='Model Runner')
    p.add_argument("-data", 
        help="Path to the data to predict should end with dataset")
    p.add_argument("-pred", 
        help="Path to the save location from the predictions")
    p.add_argument("-modelDir", 
        help="Path to the base model directory", 
        nargs='?', const="",
        default="")
    p.add_argument("-model", 
        help="Model abreviation", 
        nargs='?', const="sq3", 
        default="sq3")
    
    return p.parse_args()




def main():

    print("\n\n------------------------------")
    print("\n\nStarting Model Tester\n\n")

    args = parse_args() 
    data = args.data
    pred = args.pred
    model = args.model
    modelBaseDir = args.modelDir
    modelRunner = None

    print("data {}".format(data))
    print("pred {}".format(pred))
    print("model {}".format(model))

    # Get the Model Runner
    if model == Models.CYL.value:
        modelRunner = CylRunner(modelBaseDir)
    elif model == Models.SPV.value:
        modelRunner = SpvRunner(modelBaseDir)
    elif model == Models.SAL.value:
        modelRunner = SalRunner(modelBaseDir)
    elif model == Models.SQ3.value:
        modelRunner = Sq3Runner(modelBaseDir)
    elif model == Models.POL.value:
        modelRunner = PolRunner(modelBaseDir)
    elif model == Models.RAN.value:
        modelRunner = RanRunner(modelBaseDir)
    elif model == Models.JS3CGPU.value:
        modelRunner = JS3CGPURunner(modelBaseDir)
    elif model == Models.JS3CCPU.value:
        modelRunner = JS3CCPURunner(modelBaseDir)
    else:
        raise ValueError("Model {} not supported!".format(model))

    # Build the docker image
    modelRunner.buildDockerImage()

    # Run Prediction
    modelRunner.run(data, pred)

    print("\n\n\nDone")
        

if __name__ == '__main__':
    main()







