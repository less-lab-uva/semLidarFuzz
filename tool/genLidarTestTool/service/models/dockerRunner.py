"""
dockerRunner 
Base class for running model docker images
Inherited by other model runner classes

@Date 7/22/22
"""

import os
import subprocess


# --------------------------------------------------------------------------


class DockerRunner:
    def __init__(self, modelBaseDirectory, modelDirName):
        # Normalize modelBaseDir
        modelBaseDir = os.path.normpath(modelBaseDirectory)

        # Model information
        self.modelBaseDir = modelBaseDir
        self.modelDirName = modelDirName
        self.modelDir = modelBaseDir + "/" + modelDirName

        # Docker information
        self.container = modelDirName.lower()
        self.image = modelDirName.lower() + "_image"


    """
    Builds the docker image for the model
    """
    def buildDockerImage(self):
        if 'DO_NOT_BUILD_MODELS' in os.environ:
            print('Skipping model building based on DO_NOT_BUILD_MODELS environment var')
            return
        print("Building {}".format(self.modelDirName))


        
        # Navigate to the model directory
        dockerBuildCommand = "cd {}".format(self.modelDir)
        # Navigate to the model directory
        dockerBuildCommand += " && docker build . -t {}".format(self.image)

        subprocess.Popen(dockerBuildCommand, shell=True).wait()


    """
    Runner for a model's docker
    """
    def runModelDocker(self, dataDir, predictionDir, modelRunDir, modelRunCommand):
        print("Running {}".format(self.modelDirName))

        self.removeContainer()

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
        dockerContainer = os.environ.get('RUNNING_IN_DOCKER')
        if dockerContainer is not None:
            print('Tool is running in docker')
            dockerRunCommand += " --volumes-from {}".format(dockerContainer)
        else:
            # Bind mount the model directory
            dockerRunCommand += " --mount type=bind,source={},target={}".format(self.modelDir, self.modelDir)
            # Bind mount the data to predict
            dockerRunCommand += " --mount type=bind,source={},target={}".format(dataDir, dataDir)
            # Bind mount the location to store the predictions
            dockerRunCommand += " --mount type=bind,source={},target={}".format(predictionDir, predictionDir)
        # The image to use
        dockerRunCommand += " {}".format(self.image)
        # Command to run the model
        dockerRunCommand += " bash -c"
        # cd to where to run the command and run
        dockerRunCommand += " \"cd {} && {}\"".format(modelRunDir, modelRunCommand)

        print(dockerRunCommand)
        
        # Run the docker command
        returnCode = subprocess.Popen(dockerRunCommand, shell=True).wait()

        self.removeContainer()
        return returnCode


    """
    Removes the containers
    """
    def removeContainer(self):
        print("Attempting to Remove Container {}".format(self.modelDirName))

        # Docker Cleanup
        # dockerCleanCommand = "container stop {}".format(self.container)
        # dockerCleanCommand = " && docker container rm {}".format(self.container)
        dockerCleanCommand = "docker container stop {} && docker container rm {} 2>/dev/null".format(self.container, self.container)


        # Clean up the docker container
        subprocess.Popen(dockerCleanCommand, shell=True).wait()






