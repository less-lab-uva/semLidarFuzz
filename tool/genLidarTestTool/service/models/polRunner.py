"""
polRunner 
Runner for the PolarSeg model
pol
PolarSeg
[8 / 20]

@Date 7/22/22
"""

import os

import domain.modelConstants as modelConstants
from service.models.dockerRunner import DockerRunner

# --------------------------------------------------------------------------

class PolRunner(DockerRunner):
    def __init__(self,  modelBaseDir):
        super(PolRunner, self).__init__(modelBaseDir, modelConstants.POL_DIRECTORY_NAME)


    """
    Runs the PolarSeg docker image

    """
    def run(self, dataDirectory, predictionDirectory):
        # Normalize paths
        dataDir = os.path.normpath(dataDirectory)
        predictionDir = os.path.normpath(predictionDirectory)

        if (os.path.basename(dataDir) != "dataset"):
            raise ValueError("Expecting that the directory to predict ends with dataset {}".format(dataDir))

        # Command to run the model with
        runCommand = "python3 test_pretrain_SemanticKITTI.py"
        runCommand += " --data_dir {}".format(dataDir)
        runCommand += " --test_output_path {}".format(predictionDir)
        runCommand += " --model_save_path pretrained_weight/SemKITTI_PolarSeg.pt"

        # Location that command needs to be run from
        modelRunDir = self.modelDir

        return self.runModelDocker(dataDir, predictionDir, modelRunDir, runCommand)

    


