"""
modelValsInitial
Get the base model predictions

@Date 6/30/22
"""


from pymongo import MongoClient
import glob, os
import shutil
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
    p.add_argument("-bins", 
        help="Path to the scenes", 
        nargs='?', const="",
        default="")
    p.add_argument("-stage", 
        help="Path to the stage location", 
        nargs='?', const="",
        default="")
    p.add_argument("-pred", 
        help="Path to save the predictions made by the tools", 
        nargs='?', const="",
        default="")
    p.add_argument("-modelDir", 
        help="Path to the base model directory", 
        nargs='?', const="",
        default="")
    p.add_argument("-model", 
        help="Model name", 
        nargs='?', const="sq3", 
        default="sq3")
    
    return p.parse_args()


def main():

    print("\n\n------------------------------")
    print("\n\nStarting Model Base Prediction Maker\n\n")

    args = parse_args() 
    binBasePath = args.bins
    stagePath = args.stage
    predBasePath = args.pred
    model = args.model
    modelBaseDir = args.modelDir

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


    for x in range(0, 11):

        folderNum = str(x).rjust(2, '0')

        savePreds = predBasePath + folderNum + "/" + model + "/"
        print("\n\n\nSave At {}".format(savePreds))

        # Current folder bins
        curFolder = binBasePath + folderNum + "/velodyne"
        print("Cur folder to predict {}".format(savePreds))

        # Prepare the stage dir
        print("Removing files in stage {}:".format(stagePath))
        filelist = glob.glob(os.path.join(stagePath, "*"))
        for f in filelist:
            os.remove(f)

        # Copy bins in current folder to stage
        print("Copy folder {} to stage:".format(folderNum))
        filesInFolder = glob.glob(os.path.join(curFolder, "*")) 
        for f in filesInFolder:
            shutil.copy(f, stagePath)

        stageSeqFolder = os.path.dirname(os.path.dirname(os.path.dirname(os.path.normpath(stagePath))))

        os.makedirs(savePreds, exist_ok=True)
        
        print("Starting predictions on {}".format(folderNum))
        print("Data {}".format(stageSeqFolder))
        print("Pred {}".format(savePreds))
        print("Model {}".format(model))

        # Predict for the current folder
        returnCode = modelRunner.run(stageSeqFolder, savePreds)
        if returnCode != 0:
            print('Non-zero exit code from docker: {}'.format(returnCode))
            print('Exiting with same code')
            exit(returnCode)

    print("\n\n\nDone")
        

if __name__ == '__main__':
    main()







