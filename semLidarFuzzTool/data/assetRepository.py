"""
AssetRepository 
Handles all database interaction for assets

@Date 6/23/22
"""


import pymongo
import numpy as np

import data.fileIoUtil as fileIoUtil
import data.mongoRepository as mongoRepository

# --------------------------------------------------------------------------

class AssetRepository(mongoRepository.MongoRepository):
    def __init__(self, binPath, labelPath, mongoConnectPath):
        super(AssetRepository, self).__init__(mongoConnectPath)
        self.binPath = binPath
        self.labelPath = labelPath       
        self.assetCollection = self.db["assets4"]



    """
    Gets an asset by the id
    """
    def getAssetById(self, id):

        asset = self.assetCollection.find_one({ "_id" : id })

        return self.getInstanceFromAssetRecord(asset)



    """
    Gets a random asset from a specific sequence scene of type
    """
    def getRandomAssetWithinScene(self, sequence, scene):

        asset = self.assetCollection.aggregate([
            { "$match": { "sequence" : sequence, "scene" : scene} },
            { "$sample": { "size": 1 } }
        ])

        assetRecord = None
        try:
            assetRecord = asset.next()
        except:
            print("Get assetRecord failed")
            return None, None, None, None, None

        return self.getInstanceFromAssetRecord(assetRecord)



    """
    Gets a random asset of type
    """
    def getRandomAssetOfType(self, typeNum):

        asset = self.assetCollection.aggregate([
            { "$match": { "typeNum" : typeNum } },
            { "$sample": { "size": 1 } }
        ])

        assetRecord = None
        try:
            assetRecord = asset.next()
        except:
            print("Get assetRecord failed")
            return None, None, None, None, None

        return self.getInstanceFromAssetRecord(assetRecord)



    """
    Gets a random asset
    """
    def getRandomAsset(self):

        asset = self.assetCollection.aggregate([
            { "$sample": { "size": 1 } }
        ])

        assetRecord = None
        try:
            assetRecord = asset.next()
        except:
            print("Get assetRecord failed")
            return None, None, None, None, None

        return self.getInstanceFromAssetRecord(assetRecord)



    """
    Gets a random asset of specified types
    """
    def getRandomAssetOfTypes(self, typeNums):

        typeQuery = []
        for type in typeNums:
            typeQuery.append({"typeNum": type})

        asset = self.assetCollection.aggregate([
            { "$match": {  
                "$or":  typeQuery
            }},
            { "$sample": { "size": 1 } }
        ])

        assetRecord = None
        try:
            assetRecord = asset.next()
        except:
            print("Get assetRecord failed")
            return None, None, None, None, None

        return self.getInstanceFromAssetRecord(assetRecord)



    """
    Gets a random asset of specified types
    """
    def getRandomAssetOfTypesWithinScene(self, typeNums, sequence, scene):

        typeQuery = []
        for type in typeNums:
            typeQuery.append({"typeNum": type})

        asset = self.assetCollection.aggregate([
            { "$match": {  
                "sequence" : sequence, 
                "scene" : scene,
                "$or":  typeQuery
            }},
            { "$sample": { "size": 1 } }
        ])

        assetRecord = None
        try:
            assetRecord = asset.next()
        except:
            print("Get assetRecord failed")
            return None, None, None, None, None

        return self.getInstanceFromAssetRecord(assetRecord)



    """
    Gets the data from a given asset Record 
    """
    def getInstanceFromAssetRecord(self, assetRecord):

        instance = assetRecord["instance"]
        sequence = assetRecord["sequence"]
        scene = assetRecord["scene"]

        pcdArr, intensity, semantics, labelInstance = fileIoUtil.openLabelBin(self.binPath, self.labelPath, sequence, scene)

        maskOnlyInst = (labelInstance == instance)

        pcdArr = pcdArr[maskOnlyInst, :]
        intensity = intensity[maskOnlyInst]
        semantics = semantics[maskOnlyInst]
        labelInstance = labelInstance[maskOnlyInst]

        return pcdArr, intensity, semantics, labelInstance, assetRecord





    """
    Page Request for asset record
    Sorted by _id
    """
    def getAssetsPaged(self, page, pageLimit):
        return self.assetCollection.find({}).sort([("_id", pymongo.ASCENDING)]).skip((page - 1) * pageLimit).limit(pageLimit)











