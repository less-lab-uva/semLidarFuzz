
import shutil
from pymongo import MongoClient
import glob, os
import numpy as np
import open3d as o3d
import random
import time
import argparse

from domain.semanticMapping import name_label_mapping


globalData = {}
centerCamPoint = np.array([0, 0, 0.3])
sequences = []


# -------------------------------------------------------------

"""
Connect to mongodb 
"""
def mongoConnect(mongoConnect):
    configFile = open(mongoConnect, "r")
    mongoUrl = configFile.readline()
    print("Connecting to mongodb")
    configFile.close()
    
    client = MongoClient(mongoUrl)
    db = client["lidar_data"]
    return db



"""
formatSecondsToHhmmss
Helper to convert seconds to hours minutes and seconds
@param seconds
@return formatted string of hhmmss
"""
def formatSecondsToHhmmss(seconds):
    hours = seconds / (60*60)
    seconds %= (60*60)
    minutes = seconds / 60
    seconds %= 60
    return "%02i:%02i:%02i" % (hours, minutes, seconds)



# ------------------------------------------------------------------



def addSignInstances(scene, semantics, instances):
    
    uniqueInst = set()
    for instance in instances:
        uniqueInst.add(instance)

    maskSign = (semantics == 81) | (semantics == 80)

    onlySigns = scene[maskSign, :]
    semanticsSigns = semantics[maskSign]

    indexesSignMask = np.where(maskSign)

    # Check that there are signs 
    if (np.shape(onlySigns)[0] < 1):
        # print("NO SIGNS FOUND")
        return instances, False

    pcdSigns = o3d.geometry.PointCloud()
    pcdSigns.points = o3d.utility.Vector3dVector(onlySigns)

    labels = np.array(pcdSigns.cluster_dbscan(eps=2, min_points=10, print_progress=False))
    max_label = labels.max()
    # print(f"point cloud has {max_label + 1} clusters")

    if (max_label < 0):
        # print("NO SIGNS FOUND")
        return instances, False

    uniqueLabels = {}
    uniqueSeenLabels = set()
    for labelNum in labels:
        if (labelNum != -1 and # outliers
            labelNum not in uniqueSeenLabels): # already relabeled
            
            uniqueSeenLabels.add(labelNum)

            semanticsSign = semanticsSigns[labels == labelNum]

            types = set()
            for sem in semanticsSign:
                types.add(sem)

            if (len(types) > 1):

                pointsSign = onlySigns[labels == labelNum]
                pcdSign = o3d.geometry.PointCloud()
                pcdSign.points = o3d.utility.Vector3dVector(pointsSign)
                obb = pcdSign.get_oriented_bounding_box()
                maxXy = obb.get_max_bound()
                minXy = obb.get_min_bound()
                maxXy[2] = 0
                minXy[2] = 0
                distAcross = np.linalg.norm(maxXy - minXy)

                print("Sign across: {}".format(distAcross))

                if (distAcross < 3):

                    newLabel = 0
                    while (newLabel < 10):
                        randInstLabel = random.randint(1000, 2000)
                        if (randInstLabel not in uniqueInst):
                            uniqueLabels[labelNum] = randInstLabel
                            uniqueInst.add(randInstLabel)
                            newLabel = randInstLabel
                        else:
                            newLabel += 1


    for sign in uniqueLabels.keys():
        currentSignIndexes = indexesSignMask[0][labels == sign]
        instances[currentSignIndexes] = uniqueLabels[sign]


    return instances, True





# Asset Prechecks
def checkInclusionBasedOnTriangleMeshAsset(points, mesh):

    obb = mesh.get_oriented_bounding_box()

    legacyMesh = o3d.t.geometry.TriangleMesh.from_legacy(mesh)

    scene = o3d.t.geometry.RaycastingScene()
    _ = scene.add_triangles(legacyMesh)

    pointsVector = o3d.utility.Vector3dVector(points)

    indexesWithinBox = obb.get_point_indices_within_bounding_box(pointsVector)
    
    for idx in indexesWithinBox:
        pt = points[idx]
        query_point = o3d.core.Tensor([pt], dtype=o3d.core.Dtype.Float32)

        occupancy = scene.compute_occupancy(query_point)
        if (occupancy == 1): 
            return True

    return False


def assetIsValid(pcdArr, instances, instance, semantics):
    
    pcdsequence = o3d.geometry.PointCloud()
    pcdsequence.points = o3d.utility.Vector3dVector(pcdArr)

    instancePoints = pcdArr[instances == instance]

    # Acceptable number of points
    if (np.shape(instancePoints)[0] < 20):
        return False
    
    pcdItem = o3d.geometry.PointCloud()
    pcdItem.points = o3d.utility.Vector3dVector(instancePoints)

    # Remove asset, unlabeled, outliers, and ground (parking, road, etc)
    maskInst = (instances != instance) & (semantics != 0) & (semantics != 1) & (semantics != 40) & (semantics != 44) & (semantics != 48) & (semantics != 49) & (semantics != 60) & (semantics != 72)
    pcdWithoutInstance = pcdArr[maskInst, :]

    pcdAsset = o3d.geometry.PointCloud()
    pcdAsset.points = o3d.utility.Vector3dVector(instancePoints)

    #  Get the asset's bounding box
    obb = pcdAsset.get_oriented_bounding_box()
    assetCenter = obb.get_center()

    dist = np.linalg.norm(centerCamPoint - assetCenter)

    # Dist is acceptable
    if dist > 40:
        return False

    # There are no points obsuring this asset's bounding box

    # Scale box based on distance
    scalingFactor = (dist / 150) + 1
    # print("Scaling {} Distance {}".format(scalingFactor, dist))
    obb.scale(scalingFactor, assetCenter)

    # Get the points that comprise the box
    boxPoints = np.asarray(obb.get_box_points())

    # Take the two lowest and move z dim down (removes any floating cars)
    boxPoints = boxPoints[boxPoints[:, 2].argsort()]
    boxPoints[:2, 2] -= 5
    
    # Create new mesh with the box and the center
    boxVertices = np.vstack((boxPoints, centerCamPoint))
    pcdCastHull = o3d.geometry.PointCloud()
    pcdCastHull.points = o3d.utility.Vector3dVector(boxVertices)
    hull2, _ = pcdCastHull.compute_convex_hull()

    incuded = checkInclusionBasedOnTriangleMeshAsset(pcdWithoutInstance, hull2)
        
    return not incuded



def saveAsset(scene, sequence, instance, semantics, instances, sequenceData, assetsToSave):

    mask = (instances == instance)
    type = semantics[mask]

    typeNum = type[0]
    # Rename poles with signs to signs
    if (typeNum == 80):
        typeNum = 81
    typeName = name_label_mapping[typeNum]

    id = sequence + "-" + scene + "-" + str(instance) + "-" + typeName
    
    asset = {}
    asset["_id"] = id
    asset["sequence"] = sequence
    asset["scene"] = scene
    asset["instance"] = int(instance)
    asset["type"] = typeName
    asset["typeNum"] = int(typeNum)
    asset["points"] = int(np.shape(type)[0])
    asset["sequenceTypeNum"] = sequenceData.get(typeName, 0)

    sequenceData[typeName] = 1 + sequenceData.get(typeName, 0)
    

    assetsToSave.append(asset)

    return assetsToSave, sequenceData


def parseAssets(labelsFileName, binFileName, sequence, savePath, sequenceData, assetsToSave):

    fileName = os.path.basename(labelsFileName).replace('.label', '')

    print("Parsing: {}".format(fileName))

    # Label
    label_arr = np.fromfile(labelsFileName, dtype=np.int32)
    semantics = label_arr & 0xFFFF
    instances = label_arr >> 16 

    # Bin File
    pcdArr = np.fromfile(binFileName, dtype=np.float32)
    pcdArr = pcdArr.reshape((int(np.shape(pcdArr)[0]) // 4, 4))
    pcdArr = np.delete(pcdArr, 3, 1)

    # Extract signs add instance labels
    instances, signsFound = addSignInstances(pcdArr, semantics, instances)

    # Collect unique instances
    seenInst = set()
    for instance in instances:
        seenInst.add(instance)
    
    # Check if that instance is valid
    for instance in seenInst:

        # Skip the unlabeled asset (0)
        if (instance != 0 and assetIsValid(pcdArr, instances, instance, semantics)):
            assetsToSave, sequenceData = saveAsset(fileName, sequence, instance, semantics, instances, sequenceData, assetsToSave)


    # Save new label file with signs added
    newLabel = savePath + fileName + ".label"
    copyLabel = (labelsFileName, newLabel)
    if (signsFound):
        labelsCombined = (instances << 16) | (semantics & 0xFFFF)
        labelsCombined = labelsCombined.astype(np.int32)
        labelsCombined.tofile(newLabel)
        copyLabel = None
        

    return assetsToSave, sequenceData, copyLabel


def parseSequence(folderNum, path, savePath, mdbColAssets):

    print("Starting on seq {}".format(folderNum))
    
    currPath = path + folderNum

    saveSeqAt = savePath + folderNum + "/labels/"
    os.makedirs(saveSeqAt, exist_ok=True)

    sequenceData = {}
    sequenceData["_id"] = folderNum

    # Get label / bin files
    labelFiles = np.array(glob.glob(currPath + "/labels/*.label", recursive = True))
    binFiles = np.array(glob.glob(currPath + "/velodyne/*.bin", recursive = True))

    # Sort
    labelFiles = sorted(labelFiles)
    binFiles = sorted(binFiles)

    assetsToSave = []
    labelsToCopy = []

    for index in range(len(labelFiles)):

        assetsToSave, sequenceData, copyLabel = parseAssets(labelFiles[index], binFiles[index], folderNum, saveSeqAt, sequenceData, assetsToSave)
        if (copyLabel != None):
            labelsToCopy.append(copyLabel)

        # Batch insert
        if (len(assetsToSave) >= 2000):
            # Save the asset data
            print("Save batch of 2000 seq {}".format(folderNum))
            mdbColAssets.insert_many(assetsToSave)
            assetsToSave = []

            # Save the new label
            for labelPair in labelsToCopy:
                shutil.copyfile(labelPair[0], labelPair[1])
            labelsToCopy = []

    # Batch insert any remaining asset details
    if (len(assetsToSave) != 0):
        mdbColAssets.insert_many(assetsToSave)
    # Copy remaining labels
    if (len(labelsToCopy) != 0):
        for labelPair in labelsToCopy:
            shutil.copyfile(labelPair[0], labelPair[1])

    return sequenceData

def parse_args():
    p = argparse.ArgumentParser(
        description='Model Runner')
    p.add_argument("-binPath", 
        help="Path to the semanticKITTI sequences", 
        nargs='?', const="",
        default="")
    p.add_argument("-mdb", 
        help="Path to the mongo connect file", 
        nargs='?', const="",
        default="")
    p.add_argument("-saveAt", 
        help="Where to save the mutation results", 
        nargs='?', const=os.getcwd(), 
        default=os.getcwd())

def main():
    global globalData
    global sequences

    print("\n\n------------------------------")
    print("\n\nStarting Asset Loader\n\n")

    args = parse_args() 

    print("Connecting to Mongo")
    mdb = mongoConnect(args.mdb)
    mdbColAssets = mdb["assets4"]
    mdbColAssetMetadata = mdb["asset_metadata4"]
    print("Connected")

    path = os.path.normpath(args.binPath) + "/"
    savePath = os.path.normpath(args.saveAt) + "/"
    os.makedirs(savePath, exist_ok=True)

    print("Parsing {} :".format(path))

    # Start timer
    tic = time.perf_counter()

    sequenceResults = []

    # Parse Sequences
    for seq in range(0, 11):
        folderNum = str(seq).rjust(2, '0')
        sequenceData = parseSequence(folderNum, path, savePath, mdbColAssets)
        sequenceResults.append(sequenceData)

    
    # Save metadata for sequence
    mdbColAssetMetadata.insert_many(sequenceResults)

    # Create the global data
    for sequenceData in sequenceResults:
        for key in sequenceData.keys():
            if (key != "_id"):
                count = globalData.get(key, 0)
                globalData[key] = count + sequenceData[key]

    # Add the global data
    globalData["_id"] = "all"
    mdbColAssetMetadata.insert_one(globalData)

    # End timer
    toc = time.perf_counter()
    timeSeconds = toc - tic
    timeFormatted = formatSecondsToHhmmss(timeSeconds)

    print("Ran for {}".format(timeFormatted))

if __name__ == '__main__':
    main()



