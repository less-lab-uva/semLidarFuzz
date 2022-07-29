"""
finalDetails
Class that amalgamates the details 
Collecting analytics such as top changes and averages 

@Date 6/28/22
"""

import sys
import time

from domain.mutationsEnum import Mutation

# --------------------------------------------------------------------------


accJaccKeyList = ["accuracy", "jaccard"]


# --------------------------------------------------------------------------
# FINAL DETAILS


"""
Class to represent the final details


finalData {}
    mutation {}
        accuracy {}
            all {}
                total - int
                cyl - int
                spv - int
                sal - int
                min - float
                max - float
                avg - float
                min_cyl - float
                max_cyl - float
                avg_cyl - float
                min_spv - float
                max_spv - float
                avg_spv - float
                min_sal - float
                max_sal - float
                avg_sal - float
                avg_pointsAffected - float
                min_pointsAffected - int
                max_pointsAffected - int
            bucket_*bucketNum {}
                ... same as all {} plus
                model_overlap {}
                    cyl - int
                    spv - int
                    sal - int
                    cyl_spv - int
                    cyl_sal - int
                    spv_sal - int          
                    cyl_spv_sal - int
                    ... [All model key combos]
        jaccard {}
            ... same as accuracy
    *model {}
        mutation {}
            top_acc [size of top num]
                (detail _id, - str 
                percent change - float)
            top_jac [size of top num]
                (detail _id, - str 
                percent change - float)
    modelTime {}
        model - float
    count - int
    count_attempted - int
    seconds - str
    time - float
"""
class FinalDetails:
    def __init__(self, batchId, topNum=10, models=[], doneDir=""):
        self.finalData = {}
        self.batchId = batchId
        self.mutationsEnabled = set()
        self.topNum = topNum
        self.buckets = list(range(0, 7))
        self.duplicateSets = {}
        self.models = models
        self.prepFinalDetails()
        

        # If removing non top bins/labels
        self.doneDir = doneDir
    

    """
    Defines boundaries for buckets
    """
    def percentLossToBucket(self, percentLoss):

        bucket = 0 # percentLoss >= 0.1 %
        if (percentLoss < -5):
            bucket = 6
        elif (percentLoss < -4):
            bucket = 5
        elif (percentLoss < -3):
            bucket = 4
        elif (percentLoss < -2):
            bucket = 3
        elif (percentLoss < -1):
            bucket = 2
        elif (percentLoss < -0.1):
            bucket = 1

        return bucket



    """
    Prepares the final details dictionary preloading some of the keys
    """
    def prepFinalDetails(self):
        self.finalData = {}

        self.finalData["_id"] = self.batchId
        self.finalData["time"] = int(time.time())
        self.finalData["dateTime"] = time.ctime(time.time())

        self.finalData["mutations"] = []

        self.finalData["buckets"] = []
        for bucketNum in self.buckets:
            self.finalData["buckets"].append("bucket_" + str(bucketNum))

        # Top to save
        for model in self.models:
            self.finalData[model] = {}

        self.finalData["count"] = 0
        self.finalData["count_attempted"] = 0

        self.finalData["models"] = self.models

        self.finalData["modelTime"] = {}


    """
    Adds a new mutation to the final details dictionary preloading the keys
    """
    def addMutation(self, mutation):

        self.mutationsEnabled.add(mutation)
        self.finalData["mutations"].append(mutation)

        # Top to save
        for model in self.models:
            self.finalData[model][mutation] = {}
            self.finalData[model][mutation]["top_acc"] = []
            self.finalData[model][mutation]["top_jac"] = []

        # Accuracy and Jaccard metrics
        self.finalData[mutation] = {}
        self.finalData[mutation]["accuracy"] = {}
        self.finalData[mutation]["jaccard"] = {}
        for bucketNum in self.buckets:
            bucketKey = "bucket_" + str(bucketNum)

            # Accuracy & Jaccard
            for accJaccKey in accJaccKeyList:

                # Accuracy & Jaccard All Metrics
                self.finalData[mutation][accJaccKey]["all"] = {}
                self.finalData[mutation][accJaccKey]["all"]["total"] = 0
                self.finalData[mutation][accJaccKey]["all"]["min"] = sys.maxsize
                self.finalData[mutation][accJaccKey]["all"]["max"] = sys.maxsize * -1
                self.finalData[mutation][accJaccKey]["all"]["avg"] = 0
                for model in self.models:
                    self.finalData[mutation][accJaccKey]["all"][model] = 0
                    self.finalData[mutation][accJaccKey]["all"]["min_" + model] = sys.maxsize
                    self.finalData[mutation][accJaccKey]["all"]["max_" + model] = sys.maxsize * -1
                    self.finalData[mutation][accJaccKey]["all"]["avg_" + model] = 0
                self.finalData[mutation][accJaccKey]["all"]["min_points_affected"] = sys.maxsize
                self.finalData[mutation][accJaccKey]["all"]["max_points_affected"] = sys.maxsize * -1
                self.finalData[mutation][accJaccKey]["all"]["avg_points_affected"] = 0
                self.finalData[mutation][accJaccKey]["all"]["min_seconds"] = sys.maxsize
                self.finalData[mutation][accJaccKey]["all"]["max_seconds"] = sys.maxsize * -1
                self.finalData[mutation][accJaccKey]["all"]["avg_seconds"] = 0

                # Accuracy & Jaccard Bucket Metrics
                self.finalData[mutation][accJaccKey][bucketKey] = {}
                self.finalData[mutation][accJaccKey][bucketKey]["total"] = 0
                for model in self.models:
                    self.finalData[mutation][accJaccKey][bucketKey]["total_" + model] = 0
                    self.finalData[mutation][accJaccKey][bucketKey]["min_" + model] = sys.maxsize
                    self.finalData[mutation][accJaccKey][bucketKey]["max_" + model] = sys.maxsize * -1
                    self.finalData[mutation][accJaccKey][bucketKey]["avg_" + model] = 0
                self.finalData[mutation][accJaccKey][bucketKey]["min"] = sys.maxsize
                self.finalData[mutation][accJaccKey][bucketKey]["max"] = sys.maxsize * -1
                self.finalData[mutation][accJaccKey][bucketKey]["avg"] = 0
                self.finalData[mutation][accJaccKey][bucketKey]["min_points_affected"] = sys.maxsize
                self.finalData[mutation][accJaccKey][bucketKey]["max_points_affected"] = sys.maxsize * -1
                self.finalData[mutation][accJaccKey][bucketKey]["avg_points_affected"] = 0
                self.finalData[mutation][accJaccKey][bucketKey]["min_seconds"] = sys.maxsize
                self.finalData[mutation][accJaccKey][bucketKey]["max_seconds"] = sys.maxsize * -1
                self.finalData[mutation][accJaccKey][bucketKey]["avg_seconds"] = 0
                self.finalData[mutation][accJaccKey][bucketKey]["model_overlap"] = {}
                self.finalData[mutation][accJaccKey][bucketKey]["model_threshold_overlap"] = {}
        
        # Add new duplicate set
        self.duplicateSets[mutation] = set()
        self.finalData[mutation]["duplicates"] = 0
        self.finalData[mutation]["duplicatesPercent"] = 0



    """
    Updates the final details dictionary after a batch
    This removes the bins and labels that do not meet the save criteria (top five accuracy loss & top five jaccard loss)

    @param details list of detail dictionarys that enumerates what occured in this transformation
    @param finalData ditctionary that describes what should be saved and how many of each mutation occured
    @return finalData dictionary updated with new mutations that occured
    """
    def updateFinalDetails(self, details):

        print("Updating final details")

        potentialRemove = set()
        deleteFiles = []
        accJaccTopKeyList = ["top_acc", "top_jac"]
        
        for detail in details:
            
            # Model mutation bucket overlap 
            modelBuckets = {}
            for accJaccKey in accJaccKeyList:
                modelBuckets[accJaccKey] = {}
                for model in self.models:
                    modelBuckets[accJaccKey][model] = 0


            # Validate that the final data has this mutation
            mutation = detail["mutation"]
            if mutation not in self.mutationsEnabled:
                self.addMutation(mutation)

            # Update the duplicate counter
            self.checkForDuplicate(detail, mutation)

            # Check the accuracy of each model
            for model in self.models:

                # For both accuracy and jaccard 
                percentLossAcc = detail[model]["percentLossAcc"]
                percentLossJac = detail[model]["percentLossJac"]
                accJaccLossList = [percentLossAcc, percentLossJac]
                for i in range(0, len(accJaccTopKeyList)):

                    # Save top # for both accuracy and jaccard
                    topKey = accJaccTopKeyList[i]
                    percentLoss = accJaccLossList[i]

                    # don't have top # yet, add this mutation 
                    if (len(self.finalData[model][mutation][topKey]) < self.topNum):
                        self.finalData[model][mutation][topKey].append((detail["_id"], percentLoss))
                        self.finalData[model][mutation][topKey].sort(key = lambda x: x[1])

                    # Do have top # check against current highest, update
                    else:
                        idRemove = detail["_id"]
                            
                        # new top percent loss
                        if (self.finalData[model][mutation][topKey][4][1] > percentLoss):
                            self.finalData[model][mutation][topKey].append((detail["_id"], percentLoss))
                            self.finalData[model][mutation][topKey].sort(key = lambda x: x[1])
                            idRemove = self.finalData[model][mutation][topKey].pop()[0]
                    
                        potentialRemove.add(idRemove)


                    # Accuracy & Jaccard All & bucket metrics
                    accJaccKey = accJaccKeyList[i]

                    # Update accuracy metrics for all
                    # % Loss all
                    self.finalData[mutation][accJaccKey]["all"]["min"] = min(percentLoss, self.finalData[mutation][accJaccKey]["all"]["min"])
                    self.finalData[mutation][accJaccKey]["all"]["max"] = max(percentLoss, self.finalData[mutation][accJaccKey]["all"]["max"])
                    self.finalData[mutation][accJaccKey]["all"]["avg"] = percentLoss + self.finalData[mutation][accJaccKey]["all"]["avg"]
                    # % Loss all, model level
                    self.finalData[mutation][accJaccKey]["all"]["min_" + model] = min(percentLoss, self.finalData[mutation][accJaccKey]["all"]["min_" + model])
                    self.finalData[mutation][accJaccKey]["all"]["max_" + model] = max(percentLoss, self.finalData[mutation][accJaccKey]["all"]["max_" + model])
                    self.finalData[mutation][accJaccKey]["all"]["avg_" + model] = percentLoss + self.finalData[mutation][accJaccKey]["all"]["avg_" + model]
                    # Num points affected
                    self.finalData[mutation][accJaccKey]["all"]["min_points_affected"] = min(detail["pointsAffected"], self.finalData[mutation][accJaccKey]["all"]["min_points_affected"])
                    self.finalData[mutation][accJaccKey]["all"]["max_points_affected"] = max(detail["pointsAffected"], self.finalData[mutation][accJaccKey]["all"]["max_points_affected"])
                    self.finalData[mutation][accJaccKey]["all"]["avg_points_affected"] = detail["pointsAffected"] + self.finalData[mutation][accJaccKey]["all"]["avg_points_affected"]
                    # Time taken
                    self.finalData[mutation][accJaccKey]["all"]["min_seconds"] = min(detail["seconds"], self.finalData[mutation][accJaccKey]["all"]["min_seconds"])
                    self.finalData[mutation][accJaccKey]["all"]["max_seconds"] = max(detail["seconds"], self.finalData[mutation][accJaccKey]["all"]["max_seconds"])
                    self.finalData[mutation][accJaccKey]["all"]["avg_seconds"] = detail["seconds"] + self.finalData[mutation][accJaccKey]["all"]["avg_seconds"]


                    # Update bucket metrics for model
                    bucketNum = self.percentLossToBucket(percentLoss)
                    bucketKey = "bucket_" + str(bucketNum)
                    modelBuckets[accJaccKey][model] = bucketNum
                    # Bucket counts
                    self.finalData[mutation][accJaccKey][bucketKey]["total"] = 1 + self.finalData[mutation][accJaccKey][bucketKey]["total"]
                    self.finalData[mutation][accJaccKey][bucketKey]["total_" + model] = 1 + self.finalData[mutation][accJaccKey][bucketKey]["total_" + model]
                    # % Loss bucket level
                    self.finalData[mutation][accJaccKey][bucketKey]["min"] = min(percentLoss, self.finalData[mutation][accJaccKey][bucketKey]["min"])
                    self.finalData[mutation][accJaccKey][bucketKey]["max"] = max(percentLoss, self.finalData[mutation][accJaccKey][bucketKey]["max"])
                    self.finalData[mutation][accJaccKey][bucketKey]["avg"] = percentLoss + self.finalData[mutation][accJaccKey][bucketKey]["avg"]
                    # % Loss bucket, model level
                    self.finalData[mutation][accJaccKey][bucketKey]["min_" + model] = min(percentLoss, self.finalData[mutation][accJaccKey][bucketKey]["min_" + model])
                    self.finalData[mutation][accJaccKey][bucketKey]["max_" + model] = max(percentLoss, self.finalData[mutation][accJaccKey][bucketKey]["max_" + model])
                    self.finalData[mutation][accJaccKey][bucketKey]["avg_" + model] = percentLoss + self.finalData[mutation][accJaccKey][bucketKey]["avg_" + model]
                    # Num points affected
                    self.finalData[mutation][accJaccKey][bucketKey]["min_points_affected"] = min(detail["pointsAffected"], self.finalData[mutation][accJaccKey][bucketKey]["min_points_affected"])
                    self.finalData[mutation][accJaccKey][bucketKey]["max_points_affected"] = max(detail["pointsAffected"], self.finalData[mutation][accJaccKey][bucketKey]["max_points_affected"])
                    self.finalData[mutation][accJaccKey][bucketKey]["avg_points_affected"] = detail["pointsAffected"] + self.finalData[mutation][accJaccKey][bucketKey]["avg_points_affected"]
                    # Time taken
                    self.finalData[mutation][accJaccKey][bucketKey]["min_seconds"] = min(detail["seconds"], self.finalData[mutation][accJaccKey][bucketKey]["min_seconds"])
                    self.finalData[mutation][accJaccKey][bucketKey]["max_seconds"] = max(detail["seconds"], self.finalData[mutation][accJaccKey][bucketKey]["max_seconds"])
                    self.finalData[mutation][accJaccKey][bucketKey]["avg_seconds"] = detail["seconds"] + self.finalData[mutation][accJaccKey][bucketKey]["avg_seconds"]


            # Total count
            self.finalData[mutation]["accuracy"]["all"]["total"] = 1 + self.finalData[mutation]["accuracy"]["all"]["total"]
            self.finalData[mutation]["jaccard"]["all"]["total"] = 1 + self.finalData[mutation]["jaccard"]["all"]["total"]

            # What model landed in what bucket for this mutation (exact match and failure threshold)
            for accJaccKey in accJaccKeyList: 
                for bucketNum in self.buckets:
                    bucketKey = "bucket_" + str(bucketNum)
                    # Build overlap keys, for exact bucket matches and failure thresholds
                    exactMatch = ""
                    threshold = ""
                    for model in self.models:
                        modelBucket = modelBuckets[accJaccKey][model]
                        # Exact bucket match for this mutation accross the models
                        if (modelBucket == bucketNum):
                            if (exactMatch == ""):
                                exactMatch = model
                            else:
                                exactMatch = exactMatch + "_" + model
                        # Threshold bucket match for this mutation accross the models (they "fail" together)
                        if (modelBucket >= bucketNum):
                            if (threshold == ""):
                                threshold = model
                            else:
                                threshold = threshold + "_" + model
                    
                    # Update bucket overlap counters
                    if (exactMatch != ""):
                        curCount = self.finalData[mutation][accJaccKey][bucketKey]["model_overlap"].get(exactMatch, 0)
                        self.finalData[mutation][accJaccKey][bucketKey]["model_overlap"][exactMatch] = curCount + 1
                    if (threshold != ""):
                        curCount = self.finalData[mutation][accJaccKey][bucketKey]["model_threshold_overlap"].get(threshold, 0)
                        self.finalData[mutation][accJaccKey][bucketKey]["model_threshold_overlap"][threshold] = curCount + 1


        # Remove bin / labels that are not within the top # to save (acc & jacc)
        idInUse = set()
        for mutation in self.mutationsEnabled:
            mutation = str(mutation).replace("Mutation.", "")
            for model in self.models:
                for accJaccTopKey in accJaccTopKeyList:
                    for detailRecord in self.finalData[model][mutation][accJaccTopKey]:
                        idInUse.add(detailRecord[0])

        for idRemove in potentialRemove:
            if idRemove not in idInUse:
                labelRemove = self.doneDir + "/labels/" + idRemove + ".label"
                binRemove = self.doneDir + "/velodyne/" + idRemove + ".bin"
                deleteFiles.append(binRemove)
                deleteFiles.append(labelRemove)
                for model in self.models:
                    modelNewPredRemove = self.doneDir + "/pred/" + model + "/" + idRemove + ".label"
                    modelMutatedPredRemove = self.doneDir + "/mutatedPred/" + model + "/" + idRemove + ".label"
                    deleteFiles.append(modelNewPredRemove)
                    deleteFiles.append(modelMutatedPredRemove)

        return deleteFiles


    """
    Updates the duplicate set based on the mutation 
    """
    def checkForDuplicate(self, details, mutation):

        if mutation == Mutation.ADD_ROTATE.name:
            self.duplicateSets[mutation].add((details["asset"], details["baseSequence"], details["baseScene"], details["rotate"]))
        elif mutation == Mutation.ADD_MIRROR_ROTATE.name:
            self.duplicateSets[mutation].add((details["asset"], details["baseSequence"], details["baseScene"], details["rotate"], details["mirror"]))
        elif mutation == Mutation.SCENE_REMOVE.name:
            self.duplicateSets[mutation].add((details["asset"]))
        elif mutation == Mutation.SIGN_REPLACE.name:
            self.duplicateSets[mutation].add((details["asset"], details["sign"]))
        elif mutation == Mutation.VEHICLE_SCALE.name:
            self.duplicateSets[mutation].add((details["asset"], details["scale"]))
        elif mutation == Mutation.VEHICLE_INTENSITY.name:
            self.duplicateSets[mutation].add((details["asset"], details["intensity"]))
        elif mutation == Mutation.VEHICLE_DEFORM.name:
            self.duplicateSets[mutation].add((details["asset"], details["deformPercent"], details["deformPoint"], details["deformMu"], details["deformSigma"], details["deformSeed"]))
        else:
            print("{} not a supported mutation".format(details["mutation"]))


    """
    Collects the averages for each mutation and bucket 
    """
    def finalizeFinalDetails(self):

        for mutation in self.mutationsEnabled:

            allCount = 0

            for accJaccKey in accJaccKeyList:

                # All Avgs
                allCount = self.finalData[mutation][accJaccKey]["all"]["total"]
                if (allCount > 0):
                    self.finalData[mutation][accJaccKey]["all"]["avg"] = self.finalData[mutation][accJaccKey]["all"]["avg"] / allCount
                    self.finalData[mutation][accJaccKey]["all"]["avg_points_affected"] = self.finalData[mutation][accJaccKey]["all"]["avg_points_affected"] / allCount
                    self.finalData[mutation][accJaccKey]["all"]["avg_seconds"] = self.finalData[mutation][accJaccKey]["all"]["avg_seconds"] / allCount

                # Bucket Avgs
                for bucketNum in self.buckets:
                    bucketKey = "bucket_" + str(bucketNum)
                    bucketCountAll = self.finalData[mutation][accJaccKey][bucketKey]["total"]
                    if (bucketCountAll > 0):
                        self.finalData[mutation][accJaccKey][bucketKey]["avg"] = self.finalData[mutation][accJaccKey][bucketKey]["avg"] / bucketCountAll
                        self.finalData[mutation][accJaccKey][bucketKey]["avg_points_affected"] = self.finalData[mutation][accJaccKey][bucketKey]["avg_points_affected"] / bucketCountAll
                        self.finalData[mutation][accJaccKey][bucketKey]["avg_seconds"] = self.finalData[mutation][accJaccKey][bucketKey]["avg_seconds"] / bucketCountAll


                # Model Avgs
                for model in self.models:
                    # All model Avgs
                    allCount = self.finalData[mutation][accJaccKey]["all"]["total"]
                    if (allCount > 0):
                        self.finalData[mutation][accJaccKey]["all"]["avg_" + model] = self.finalData[mutation][accJaccKey]["all"]["avg_" + model] / allCount

                    # Bucket model Avgs
                    for bucketNum in self.buckets:
                        bucketKey = "bucket_" + str(bucketNum)
                        bucketCountModel = self.finalData[mutation][accJaccKey][bucketKey]["total_" + model]
                        if (bucketCountModel > 0):
                            self.finalData[mutation][accJaccKey][bucketKey]["avg_" + model] = self.finalData[mutation][accJaccKey][bucketKey]["avg_" + model] / bucketCountModel


            # Get duplicate counts
            duplicates = (allCount - len(self.duplicateSets[mutation]))
            self.finalData[mutation]["duplicates"] = duplicates
            if (allCount > 0):
                self.finalData[mutation]["duplicatesPercent"] = (duplicates / allCount) * 100


        return self.finalData


    """
    Sets the time for the final details
    """
    def setTime(self, timeSeconds, timeFormatted):
        self.finalData["seconds"] = timeSeconds
        self.finalData["time"] = timeFormatted


    """
    Sets the attempts for the final details
    """
    def setAttempts(self, successCount, attemptCount):
        self.finalData["count"] = successCount
        self.finalData["count_attempted"] = attemptCount
        self.finalData["percent_success"] = 0
        if (attemptCount > 0):
            self.finalData["percent_success"] = (successCount / attemptCount) * 100
            

    """
    Sets the attempts for the final details
    """
    def setAttempts(self, successCount, attemptCount):
        self.finalData["count"] = successCount
        self.finalData["count_attempted"] = attemptCount
        self.finalData["percent_success"] = 0
        if (attemptCount > 0):
            self.finalData["percent_success"] = (successCount / attemptCount) * 100



    def updateModelTime(self, modelTimeDict):
        for model in self.models:
            modelTime = modelTimeDict.get(model, 0.0)
            curTime = self.finalData["modelTime"].get(model, 0.0)
            self.finalData["modelTime"][model] = modelTime + curTime


