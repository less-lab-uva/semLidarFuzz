"""
sq3Runner 
Runner for the SqueezeSegV3 model
sq3
SqueezeSegV3
[7 / 15]

@Date 7/22/22
"""

import os

import domain.modelConstants as modelConstants
from service.models.dockerRunner import DockerRunner

# --------------------------------------------------------------------------

class Sq3Runner(DockerRunner):
    def __init__(self,  modelBaseDir):
        super(Sq3Runner, self).__init__(modelBaseDir, modelConstants.SQ3_DIRECTORY_NAME)


    """
    Runs the SqueezeSegV3 docker image

    """
    def run(self, dataDirectory, predictionDirectory):
        # Normalize paths
        dataDir = os.path.normpath(dataDirectory)
        predictionDir = os.path.normpath(predictionDirectory)

        if (os.path.basename(dataDir) != "dataset"):
            raise ValueError("Expecting that the directory to predict ends with dataset {}".format(dataDir))

        # Command to run the model with
        runCommand = "python3 demo.py"
        runCommand += " --dataset {}".format(dataDir)
        runCommand += " --log {}".format(predictionDir)
        runCommand += " --model {}/SSGV3-53".format(self.modelDir)

        # Location that command needs to be run from
        modelRunDir = self.modelDir + "/src/tasks/semantic"

        return self.runModelDocker(dataDir, predictionDir, modelRunDir, runCommand)

    


