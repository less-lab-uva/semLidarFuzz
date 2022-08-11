"""
js3cGPURunner
Runner for the JSC3-Net model on the gpu
js3cgpu
JSC3-Net
[1 / 3]

@Date 8/7/22
"""

import os

import domain.modelConstants as modelConstants
from service.models.dockerRunner import DockerRunner


# --------------------------------------------------------------------------

class JS3CGPURunner(DockerRunner):
    def __init__(self, modelBaseDir):
        super(JS3CGPURunner, self).__init__(modelBaseDir, modelConstants.JS3CGPU_DIRECTORY_NAME)

    """
    Runs the cylinder3d docker image

    """

    def run(self, dataDirectory, predictionDirectory):
        # Normalize paths
        dataDir = os.path.normpath(dataDirectory)
        predictionDir = os.path.normpath(predictionDirectory)

        if (os.path.basename(dataDir) != "dataset"):
            raise ValueError("Expecting that the directory to predict ends with dataset {}".format(dataDir))

        # Command to run the model with
        # $ python test_kitti_segment.py --log_dir JS3C-Net-kitti --gpu 0 --dataset [val/test]
        runCommand = "python3 test_kitti_segment.py"
        runCommand += " --gpu 0"
        runCommand += " --labels {}".format(dataDir)
        runCommand += " --output_dir {}".format(predictionDir)
        runCommand += " --dataset test"

        # Location that command needs to be run from
        modelRunDir = self.modelDir

        return self.runModelDocker(dataDir, predictionDir, modelRunDir, runCommand)




