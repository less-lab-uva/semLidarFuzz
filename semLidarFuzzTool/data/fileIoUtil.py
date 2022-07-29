"""
fileIoUtil 
Handles the file operations to get and save labels and bins

@Date 6/23/22
"""

import numpy as np
import os
import glob


# --------------------------------------------------------------------------
# SAVE


"""
Saves a modified bin file and label file
Rejoins xyz & intensity for bin file 
Rejoins semantics & instance for label file 
"""
def saveBinLabelPair(xyz, intensity, semantics, instances, saveBinPath, saveLabelPath, fileName):

    # Combine labels
    labelsCombined = (instances << 16) | (semantics & 0xFFFF)

    # Combine bin
    xyzi = np.c_[xyz, intensity]
    xyziFlat = xyzi.flatten()

    # Create the file path to save
    binFile = saveBinPath + fileName + ".bin"
    labelFile = saveLabelPath + fileName + ".label"

    # Make sure the type is correct before it is saved
    xyziFlat = xyziFlat.astype(np.float32)
    labelsCombined = labelsCombined.astype(np.int32)

    # Save
    xyziFlat.tofile(binFile)
    labelsCombined.tofile(labelFile)



def saveLabelSemantics(semantics, saveLabelPath, fileName):
    # Create empty instances
    instances = np.zeros(np.shape(semantics)[0], np.int32)

    # Combine labels
    labelsCombined = (instances << 16) | (semantics & 0xFFFF)

    # Create the file path to save
    labelFile = saveLabelPath + fileName + ".label"

    # Make sure the type is correct before it is saved
    labelsCombined = labelsCombined.astype(np.int32)

    # Save
    labelsCombined.tofile(labelFile)



# --------------------------------------------------------------------------
# OPEN


"""
openLabelBin
For a specific sequence and scene
Opens a bin and label file splitting between xyz, intensity, semantics, instances 
"""
def openLabelBin(pathVel, pathLabel, sequence, scene):

    folderNum = str(sequence).rjust(2, '0')
    currPathVel = pathVel + "/" + folderNum
    currPathLbl = pathLabel + "/" + folderNum

    binFile = currPathVel + "/velodyne/" + scene + ".bin"
    labelFile = currPathLbl + "/labels/" + scene + ".label"

    return openLabelBinFiles(binFile, labelFile)



"""
openLabelBinFiles
Opens a bin and label file splitting between xyz, intensity, semantics, instances 
"""
def openLabelBinFiles(binFile, labelFile):
    # Label
    semantics, instances = openLabelFile(labelFile)

    # Bin File
    pcdArr = np.fromfile(binFile, dtype=np.float32)
    pcdArr = pcdArr.reshape((int(np.shape(pcdArr)[0]) // 4, 4))
    
    intensity = pcdArr[:, 3]
    pcdArr = np.delete(pcdArr, 3, 1)

    return pcdArr, intensity, semantics, instances



"""
openLabelBin
For a specific sequence and scene
Opens a bin and label file splitting between xyz, intensity, semantics, instances 
"""
def openLabel(pathLabel, sequence, scene):

    folderNum = str(sequence).rjust(2, '0')
    currPathLbl = pathLabel + "/" + folderNum

    labelFile = currPathLbl + "/labels/" + scene + ".label"

    return openLabelFile(labelFile)




"""
openLabelBin
For a specific sequence and scene
Opens a bin and label file splitting between xyz, intensity, semantics, instances 
"""
def openLabelFile(labelFile):
    # Label
    label_arr = np.fromfile(labelFile, dtype=np.int32)
    semantics = label_arr & 0xFFFF
    instances = label_arr >> 16 

    return semantics, instances





"""
openModelLabels
Opens the model label prediction file
"""
def openModelPredictions(modelPath, model, sequence, scene):
    
    folderNum = str(sequence).rjust(2, '0')
    predFile = modelPath + "/" + folderNum + "/" + model + "/" + scene + ".label"

    # Get Model's Prediction
    prediction, _ = openLabelFile(predFile)

    return prediction




"""
Setup step to get all scenes scan / label paths
"""
def getBinsLabels(binPath, labelPath):

    binFiles = []
    labelFiles = []
    
    for sequenceNum in range(0, 11):
        
        folderNum = str(sequenceNum).rjust(2, '0')
        currBinPath = binPath + "/" + folderNum
        currLabelPath = labelPath + "/" + folderNum

        binFilesSequence = np.array(glob.glob(currBinPath + "/velodyne/*.bin", recursive = True))
        labelFilesSequence = np.array(glob.glob(currLabelPath + "/labels/*.label", recursive = True))
        
        # Sort
        labelFilesSequence = sorted(labelFilesSequence)
        binFilesSequence = sorted(binFilesSequence)
        
        for labelFile in labelFilesSequence:
            labelFiles.append(labelFile)
        
        for binFile in binFilesSequence:
            binFiles.append(binFile)

    return binFiles, labelFiles



# --------------------------------------------------------------------------
# DELETE

    

"""
Attempts to remove files
"""
def removeFiles(files):
    for file in files:
        try:
            os.remove(file)
        except OSError:
            print("File {} not found when calling remove".format(file))








