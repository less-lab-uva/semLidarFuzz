"""
redoMutation
Recreates the mutation results for specific details

@Date 6/29/22
"""


import json

import controllers.mutationTool.mutationRunner as mutationRunner


from data.mutationDetailsRepository import DetailsRepository
from data.assetRepository import AssetRepository
from data.finalDataRepository import FinalDataRepository
from service.eval.finalDetails import FinalDetails


# -------------------------------------------------------------

PAGE_LIMIT = 1000

# -------------------------------------------------------------


"""
batchRecreation
Get details by a batch Id then save
"""
def batchRecreation(batchId, sessionManager):
    print("\n\n LiDAR Test Recreation")
    print("Recreating Batch: {}".format(batchId))

    # Connect to collections
    detailsRepository = DetailsRepository(sessionManager.mongoConnect)
    assetRepo = AssetRepository(sessionManager.binPath, sessionManager.binPath, sessionManager.mongoConnect)
    finalDataRepo = FinalDataRepository(sessionManager.mongoConnect)

    # Create a final data
    finalData = FinalDetails(sessionManager.batchId, 
                        topNum=sessionManager.saveNum, 
                        models=sessionManager.models, 
                        doneDir=sessionManager.doneDir)

    page = 0
    parsed = 0
    successNum = 0
    batchCount = 0
    mutationDetails = []
    
    total = detailsRepository.countMutationDetailsBatchId(batchId)
    print("Total count for batchId {} is {}".format(batchId, total))

    # Parse the details in the batch
    while (parsed < total):

        page += 1
        print("Parsing details on page {} of size {}".format(page, PAGE_LIMIT))
        detailsCursor = detailsRepository.getMutationDetailsPaged(batchId, page, PAGE_LIMIT)

        detailsList = list(detailsCursor)
        count = len(detailsList)
        parsed += count
        print("Found {} on page {}, {}/{}".format(count, page, parsed, total))
        for details in detailsList:
            success = False
            success, detailsNew = recreateOne(details, assetRepo, sessionManager)

            # Save batch
            if success:
                successNum += 1
                batchCount += 1
                detailsNew["recreationId"] = details["_id"]
                mutationDetails.append(detailsNew)
                print(json.dumps(detailsNew, indent=4))
            else:
                print("Could not successfully recreate {} in batch {}".format(details["_id"], batchId))


            if (len(mutationDetails) == sessionManager.batchNum):
                finalData = mutationRunner.evalBatch(sessionManager, mutationDetails, finalData, successNum, sessionManager.expectedNum)
                mutationDetails = []


        # Catch in case there was an error
        if (count == 0):
            total = parsed

    # Catch if batch didn't match up
    if (len(mutationDetails) > 0):
        finalData = mutationRunner.evalBatch(sessionManager, mutationDetails, finalData, successNum, sessionManager.expectedNum)
        mutationDetails = []


    # Output final data
    print()
    print(json.dumps(finalData.finalData, indent=4))
    print()

    if (sessionManager.evalMutationFlag):
        finalData.finalizeFinalDetails()
        finalDataRepo.saveFinalData(finalData.finalData)

    # Save final data
    if (sessionManager.saveMutationFlag):
        with open(sessionManager.dataDir + '/finalData.json', 'w') as outfile:
            json.dump(finalData.finalData, outfile, indent=4, sort_keys=True)



"""
mutationRecreation
Get a detail by Id then save
"""
def mutationRecreation(mutationId, sessionManager):
    print("\n\n LiDAR Test Generation Recreation")
    print("Recreating Mutation {}".format(mutationId))

    # Recreate

    # Get one recreate
    detailsRepository = DetailsRepository(sessionManager.mongoConnect)

    details = detailsRepository.getMutationDetailsById(mutationId)

    assetRepo = AssetRepository(sessionManager.binPath, sessionManager.binPath, sessionManager.mongoConnect)
    success, detailsNew = recreateOne(details, assetRepo, sessionManager)

    # Save
    if (not success):
        print("Could not successfully recreate {}".format(mutationId))
        exit()
    
    print(json.dumps(detailsNew, indent=4))

    # Eval

    # Create a final data
    finalData = FinalDetails(sessionManager.batchId, 
                        topNum=sessionManager.saveNum, 
                        models=sessionManager.models, 
                        doneDir=sessionManager.doneDir)

    finalData = mutationRunner.evalBatch(sessionManager, [detailsNew], finalData, 1, sessionManager.expectedNum)

    # Output final data
    print()
    print(json.dumps(finalData.finalData, indent=4))
    print()


    # Save final data
    if (sessionManager.saveMutationFlag):
        with open(sessionManager.dataDir + '/finalData.json', 'w') as outfile:
            json.dump(finalData.finalData, outfile, indent=4, sort_keys=True)



"""
recreateOne
Given a detail prepare the session to recreate this mutation then perform the mutation
"""
def recreateOne(details, assetRepo, sessionManager):
    print("Recreating {}".format(details["_id"]))

    # Base scene
    sessionManager.scene = details.get("baseScene", None)
    sessionManager.sequence = details.get("baseSequence", None)

    # Asset
    sessionManager.assetId = details.get("asset", None)

    # Rotate
    sessionManager.rotation = details.get("rotate", None)
    # Mirror
    sessionManager.mirrorAxis = details.get("mirror", None)
    # Scale
    sessionManager.scaleAmount = details.get("scale", None)
    # Sign Change
    sessionManager.signChange = details.get("sign", None)
    # Deform
    sessionManager.deformPercent = details.get("deformPercent", None)
    sessionManager.deformPoint = details.get("deformPoint", None)
    sessionManager.deformMu = details.get("deformMu", None)
    sessionManager.deformSigma = details.get("deformSigma", None)
    sessionManager.deformSeed = details.get("deformSeed", None)
    # Intensity
    sessionManager.intensity = details.get("intensity", None)


    return mutationRunner.performMutation(details["mutation"], assetRepo, sessionManager)


