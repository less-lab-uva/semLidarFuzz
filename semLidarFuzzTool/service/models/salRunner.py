"""
salRunner 
Runner for the SalsaNext model
sal
SalsaNext
[5 / 11]

@Date 7/22/22
"""

import os

import domain.modelConstants as modelConstants
from service.models.dockerRunner import DockerRunner

# --------------------------------------------------------------------------

class SalRunner(DockerRunner):
    def __init__(self,  modelBaseDir):
        super(SalRunner, self).__init__(modelBaseDir, modelConstants.SAL_DIRECTORY_NAME)


    """
    Runs the SalsaNext docker image

    """
    def run(self, dataDirectory, predictionDirectory):
        # Normalize paths
        dataDir = os.path.normpath(dataDirectory)
        predictionDir = os.path.normpath(predictionDirectory)

        if (os.path.basename(dataDir) != "dataset"):
            raise ValueError("Expecting that the directory to predict ends with dataset {}".format(dataDir))

        # Command to run the model with
        runCommand = "python3 infer.py"
        runCommand += " -d {}".format(dataDir)
        runCommand += " -l {}".format(predictionDir)
        runCommand += " -m {}/pretrained".format(self.modelDir)
        runCommand += " -s test -c 1"

        # Location that command needs to be run from
        modelRunDir = self.modelDir + "/train/tasks/semantic"

        self.runModelDocker(dataDir, predictionDir, modelRunDir, runCommand)

    


