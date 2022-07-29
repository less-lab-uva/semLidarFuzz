"""
spvRunner 
Runner for the spvnas model
spv
spvnas
[2 / 4]

@Date 7/22/22
"""

import os

import domain.modelConstants as modelConstants
from service.models.dockerRunner import DockerRunner

# --------------------------------------------------------------------------

class SpvRunner(DockerRunner):
    def __init__(self,  modelBaseDir):
        super(SpvRunner, self).__init__(modelBaseDir, modelConstants.SPV_DIRECTORY_NAME)


    """
    Runs the spvnas docker image
    """
    def run(self, dataDirectory, predictionDirectory):
        # Normalize paths
        dataDir = os.path.normpath(dataDirectory)
        predictionDir = os.path.normpath(predictionDirectory)

        if (os.path.basename(dataDir) != "dataset"):
            raise ValueError("Expecting that the directory to predict ends with dataset {}".format(dataDir))

        # Command to run the model with
        runCommand = "torchpack dist-run"
        runCommand += " -np 1 python3 evaluate.py configs/semantic_kitti/default.yaml"
        runCommand += " --name SemanticKITTI_val_SPVNAS@65GMACs"
        runCommand += " --data-dir {}/sequences/".format(dataDir)
        runCommand += " --save-dir {}".format(predictionDir)

        # Location that command needs to be run from
        modelRunDir = self.modelDir

        self.runModelDocker(dataDir, predictionDir, modelRunDir, runCommand)

    


