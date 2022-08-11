"""
ranRunner 
Runner for the RandLA-Net model
ran
RandLA-Net
[9 / 21]

@Date 7/22/22
"""

import os
import subprocess

import domain.modelConstants as modelConstants
from service.models.dockerRunner import DockerRunner

# --------------------------------------------------------------------------

class RanRunner(DockerRunner):
    def __init__(self,  modelBaseDir):
        super(RanRunner, self).__init__(modelBaseDir, modelConstants.RAN_DIRECTORY_NAME)


    """
    Runs the RandLA-Net docker image

    """
    def run(self, dataDirectory, predictionDirectory):
        # Normalize paths
        dataDir = os.path.normpath(dataDirectory)
        predictionDir = os.path.normpath(predictionDirectory)

        if (os.path.basename(dataDir) != "dataset"):
            raise ValueError("Expecting that the directory to predict ends with dataset {}".format(dataDir))

        # Command to create the graphs the model uses for predictions
        runCommand = "python3 utils/data_prepare_semantickitti.py"
        runCommand += " --dataset {}/sequences".format(dataDir)

        # Command to run the model with
        runCommand +=" && python3 -B main_SemanticKITTI.py --gpu 0 --mode test --test_area 00"
        runCommand +=" --model_path {}/SemanticKITTI/snap-277357".format(self.modelDir)
        runCommand +=" --dataset {}/sequences_0.06".format(dataDir)
        runCommand +=" --saveAt {}".format(predictionDir) 

        # Extra portion of the command to remove the graphs created
        runCommand +=" && rm -rf {}/sequences_0.06".format(dataDir)

        # Location that command needs to be run from
        modelRunDir = self.modelDir

        return self.runModelDocker(dataDir, predictionDir, modelRunDir, runCommand)


    """
    buildDockerImage

    This requires a unique build because
    RandLa has custom operators that need to compiled 
    Locally where the model is going to be run from
    With access to the GPU
    """
    def buildDockerImage(self):
        print("Building RandLa-Net Docker Custom")
        super().buildDockerImage()

        # Create the docker run command
        dockerRunCommand = "docker run" 
        # Name of the container to create
        dockerRunCommand += " --name {}".format(self.container)
        # allow the container to use the machines GPUs
        dockerRunCommand += " --gpus all"
        # Use this user so that files can be moved / removed 
        dockerRunCommand += " --user {}".format(os.getuid())
        # Prevents an out of memory error for some models
        dockerRunCommand += " --ipc=host"
        # Bind mount the model directory
        dockerRunCommand += " --mount type=bind,source={},target={}".format(self.modelDir, self.modelDir)
        # The image to use
        dockerRunCommand += " {}".format(self.image)
        # Command to run the model
        dockerRunCommand += " bash -c"
        # cd to where to run the command and Compile the custom operators
        dockerRunCommand += " \"cd {} && sh compile_op.sh\"".format(self.modelDir)

        subprocess.Popen(dockerRunCommand, shell=True).wait()

        super().removeContainer()

