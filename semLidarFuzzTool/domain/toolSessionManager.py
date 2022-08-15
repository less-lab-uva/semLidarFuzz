"""
toolSessionManager 
Manages a given run of the semantic LiDAR fuzzer tool

@Date 6/28/22
"""

import numpy as np
import glob, os
import shutil
import shortuuid


import data.fileIoUtil as fileIoUtil

from domain.mutationsEnum import Mutation
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


class SessionManager:
    def __init__(self, args):

        print("---------------------------------------------")
        print("Semantic LiDAR Fuzzer")

        # Create a batch id for this run
        self.batchId = str(shortuuid.uuid())
        print("BatchId {}".format(self.batchId))

        # ------------------------------------------
        # Required Paths

        # Mongo connection URL
        self.mongoConnect = args.mdb

        # Required paths
        self.binPath = os.path.normpath(args.binPath)
        self.labelPath = os.path.normpath(args.labelPath)
        self.basePredictionPath = os.path.normpath(args.predPath)
        self.modelDir = os.path.normpath(args.modelDir)
        self.saveAt = os.path.normpath(args.saveAt)

        print("\nProvided Paths:")
        print("MongoConnect: {}".format(self.mongoConnect))
        print("ModelDirectory: {}".format(self.modelDir))
        print("Scan Bin Path: {}".format(self.binPath))
        print("Label Path: {}".format(self.labelPath))
        print("Original Prediction Path: {}".format(self.basePredictionPath))
        print("Saving Results at: {}".format(self.saveAt))

        # Get the bins and labels
        self.binFiles = []
        self.labelFiles = []
        self.binFiles, self.labelFiles = fileIoUtil.getBinsLabels(self.binPath, self.labelPath)

        self.thread_count = args.thread_count
        print('Running on {} thread(s)'.format(self.thread_count))

        # ------------------------------------------
        # For this Run what is occuring
      
        # Get the models in use for this run
        self.models = self.prepareModels(args.models)

        # Mutations to choose from
        self.mutationsEnabled = self.prepareMutations(args.mutation)

        # Batch and total counts
        self.expectedNum = int(args.count)
        self.batchNum = int(args.batch)

        # How many to save
        self.saveAll = args.saveAll
        self.saveNum = args.saveNum

        print("\nRunning with:")
        print("Models: {}".format(self.models))
        print("Mutations: {}".format(self.mutationsEnabled))
        print("Total Mutation Count: {}".format(self.expectedNum))
        print("Batching Eval Every: {}".format(self.batchNum))
        if (self.saveAll):
            print("Saving ALL Mutations")
        else:
            print("Saving Top Mutations: {}".format(self.saveNum))

        # ------------------------------------------
        # Optional Params

        # Flag to use open3d to visualize the mutation
        self.visualize = args.vis

        # Flag for removal to attempt to itterate through all assets
        self.removeIterate = not args.removeRandom
        self.removeIterateNum = 0

        # Specific asset
        self.assetId = args.assetId

        # Set the base scene to be one specific seq / scene for ADD
        self.sequence = args.sequence
        self.scene = args.scene
        if ((self.sequence != None and self.scene == None) or
            (self.sequence == None and self.scene != None)):
            print("Sequence {} / Scene {}, Both must be provided!".format(self.sequence, self.scene))
            exit()
        
        # Makes the evaluation asyncronous from mutation generation
        self.asyncEval = args.asyncEval

        # Flags for convience 
        self.saveMutationFlag = args.ns
        self.evalMutationFlag = args.ne and self.saveMutationFlag


        # Print the optional params in use
        print("\nOptional Params")
        if (self.visualize):
            print("Visualizing")
        if (self.removeIterate):
            print("Remove will iterate through assets (not randomly select)")
        if (self.assetId != None):
            print("AssetId: {}".format(self.assetId))
        if (self.scene != None):
            print("Sequence {} / Scene {} for ADD".format(self.sequence, self.scene))
        if self.asyncEval:
            print("Evaluation Asyncronous")
        if not self.saveMutationFlag:
            print("Saving disabled")
        if not self.evalMutationFlag:
            print("Evaluation disabled")


        # ------------------------------------------
        # Paths to the directories where specific things are stored

        self.stageDir = ""
        self.currentDatasetDir = ""
        self.resultDir = ""
        self.currentVelDir = ""
        self.doneVelDir = ""
        self.evalDir = ""
        self.dataDir = ""
        self.doneDir = ""
        self.doneLabelDir = ""
        self.donePredDir = ""
        self.doneMutatedPredDir = ""

        if (self.saveMutationFlag):
            print("\nSetting up result folder pipeline")
            self.setUpDataFolders()

        if self.evalMutationFlag:
            print("\nBuilding Images for models in use")
            self.buildModels(self.models)

        # ------------------------------------------
        # Recreation Params

        self.rotation = args.rotate
        self.mirrorAxis = args.mirror
        self.intensityChange = args.intensity
        self.scaleAmount = args.scale
        self.signChange = args.sign
        self.deformPercent = args.deformPercent
        self.deformPoint = args.deformPoint
        self.deformMu = args.deformMu
        self.deformSigma = args.deformSigma
        self.deformSeed = args.deformSeed

        self.redoBatchId = args.redoBatchId
        self.redoMutationId = args.redoMutationId




    """
    Builds the docker images for the models
    """
    def buildModels(self, models):
        for model in models:
            # Get the Model Runner
            if model == Models.CYL.value:
                modelRunner = CylRunner(self.modelDir)
            elif model == Models.SPV.value:
                modelRunner = SpvRunner(self.modelDir)
            elif model == Models.SAL.value:
                modelRunner = SalRunner(self.modelDir)
            elif model == Models.SQ3.value:
                modelRunner = Sq3Runner(self.modelDir)
            elif model == Models.POL.value:
                modelRunner = PolRunner(self.modelDir)
            elif model == Models.RAN.value:
                modelRunner = RanRunner(self.modelDir)
            elif model == Models.JS3CGPU.value:
                modelRunner = JS3CGPURunner(self.modelDir)
            elif model == Models.JS3CCPU.value:
                modelRunner = JS3CCPURunner(self.modelDir)
            else:
                raise ValueError("Model {} not supported!".format(model))

            # Build the docker image
            modelRunner.buildDockerImage()


    """
    Selects the mutations that will be in use
    """
    def prepareMutations(self, mutationsGiven):
        # Get mutations to use
        mutations = []
        if (mutationsGiven == None):
            mutations = [Mutation.ADD_ROTATE]

        else:
            for mutation in mutationsGiven.split(","):
                try:
                    mutantToAdd = Mutation[mutation]
                except KeyError:
                    print("%s is not a valid option" % (mutation))
                    exit()
                mutations.append(mutantToAdd)

            

        return mutations


    """
    Selects the models that will be in use
    """
    def prepareModels(self, modelsGiven):

        # Set of valid models names
        modelValues = []
        for model in Models:
            modelValues.append(model.value)
        modelSet = set(modelValues)

        # Get models to use
        models = []
        
        if (modelsGiven == None):
            models = [Models.CYL.value]
        else:
            for model in modelsGiven.split(","):
                if (model not in modelSet):
                    print("%s is not a valid option" % (model))
                    exit()
                models.append(model)

        return models
        



    def setUpDataFolders(self):

        """
        /output
            /staging
            /current/dataset/sequences/00/velodyne
            /results
                /cyl
                /spv
                /sal/sequences/00
                /sq3/sequences/00
                /dar/sequences/00
            /done
                /velodyne
                /labels
                /pred
                    /cyl
                    /spv
                    /sal
                    /sq3
                    /dar
                /mutatedPred
                    /cyl
                    /spv
                    /sal
                    /sq3
                    /dar
        """

        # make a top level output dir
        self.dataDir = self.saveAt + "/output"
        isExist = os.path.exists(self.dataDir)
        if not isExist:
            os.makedirs(self.dataDir)

        """
        /output
            /staging
        """

        # staging
        self.stageDir = self.dataDir + "/staging"
        if os.path.exists(self.stageDir):
            shutil.rmtree(self.stageDir)
            print("Removing {}".format(self.stageDir))     
        os.makedirs(self.stageDir)


        """
        /output
            /current/dataset/sequences/00/velodyne
        """

        # The directory that the models use to evaluate the bins
        self.currentDatasetDir = self.dataDir + "/current/dataset"
        currentDir = self.currentDatasetDir + "/sequences/00"
        os.makedirs(currentDir, exist_ok=True)
        self.currentVelDir = currentDir + "/velodyne"
        if os.path.exists(self.currentVelDir):
            shutil.rmtree(self.currentVelDir)
            print("Removing {}".format(self.currentVelDir))
        os.makedirs(self.currentVelDir)

        """
        /output
            /results
                /cyl
                /spv
                /sal/sequences/00
        """

        # results
        self.resultDir = self.dataDir + "/results"
        isExist = os.path.exists(self.resultDir)
        if not isExist:
            os.makedirs(self.resultDir)

        # Set up model save directories
        for model in self.models:
            resultModelDir = self.resultDir + "/" + model
            if os.path.exists(resultModelDir):
                shutil.rmtree(resultModelDir)
                print("Removing {}".format(resultModelDir))
            os.makedirs(resultModelDir)


        """
        /output
            /done
                /velodyne
                /labels
                /pred
                    /cyl
                    /spv
                    /sal
                /mutatedPred
                    /cyl
                    /spv
                    /sal
        """

        # done
        self.doneDir = self.dataDir + "/done"
        if os.path.exists(self.doneDir):
            shutil.rmtree(self.doneDir, ignore_errors=True)
            print("Removing {}".format(self.doneDir))
        os.makedirs(self.doneDir)
        
        # done
        self.doneVelDir = self.doneDir + "/velodyne"
        isExist = os.path.exists(self.doneVelDir)
        if not isExist:
            os.makedirs(self.doneVelDir)

        # labels
        self.doneLabelDir = self.doneDir + "/labels"
        isExist = os.path.exists(self.doneLabelDir)
        if not isExist:
            os.makedirs(self.doneLabelDir)

        # Prediction labels done
        self.donePredDir = self.doneDir + "/pred"
        isExist = os.path.exists(self.donePredDir)
        if not isExist:
            os.makedirs(self.donePredDir)
        
        for model in self.models:
            # Models done
            donePredModelDir = self.donePredDir + "/" + model
            isExist = os.path.exists(donePredModelDir)
            if not isExist:
                os.makedirs(donePredModelDir)

        # Mutated Prediction labels done
        self.doneMutatedPredDir = self.doneDir + "/mutatedPred"
        isExist = os.path.exists(self.doneMutatedPredDir)
        if not isExist:
            os.makedirs(self.doneMutatedPredDir)
        
        for model in self.models:
            # Models done
            doneMutatedPredModelDir = self.doneMutatedPredDir + "/" + model
            isExist = os.path.exists(doneMutatedPredModelDir)
            if not isExist:
                os.makedirs(doneMutatedPredModelDir)





