


from rangeImageFinalVis import LaserScanVis, SemLaserScan
import numpy as np
import glob, os
import argparse
import shutil
from pymongo import MongoClient
import json
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 


from data.mutationDetailsRepository import DetailsRepository

from domain.semanticMapping import color_map_alt_bgr

# --------------------------------------------------------------------------------

dataDir = ""
labelsDir = ""
toolDir = ""
finalVisDir = ""
predDir = ""

dedup = set()
mutations = set()

scan = None
vis = None



# --------------------------------------------------------------------------------


def setUpSaveDir(finalData, saveDir):
    global finalVisDir
    global mutations
    global models

    """
    /finalvis
        /mutation
            /mutationId
                og-id : original scan with original labels
                new-id : new scan with new labels
                og-model-id : original scan with model labels (x3)
                og-model-asset-id : original asset scan with model labels (x3)
                new-model-id : new scan with model labels (x3)
            mutationId : combined mutation range images
    """

    
    finalVisDir = saveDir + "/finalvis"
    if os.path.exists(finalVisDir):
        shutil.rmtree(finalVisDir, ignore_errors=True)
        print("Removing {}".format(finalVisDir))
    os.makedirs(finalVisDir, exist_ok=True)

    mutations = set()

    for mutation in finalData[models[0]].keys():
        os.makedirs(finalVisDir + "/" + mutation, exist_ok=True)
        mutations.add(mutation)

    ids = set()

    for mutation in mutations:
        for model in models:
            for key in finalData[model][mutation].keys():
                if ("top" in key):
                    for mutationId in finalData[model][mutation][key]:
                        if (mutationId[0] not in ids):
                            os.makedirs(finalVisDir + "/" + mutation + "/" + mutationId[0], exist_ok=True)
                            ids.add(mutationId[0])



def getDiffImage(groundTruth, expected, newPred):
    gtImg = np.asarray(Image.open(groundTruth))
    expectedImg = np.asarray(Image.open(expected))
    newImg = np.asarray(Image.open(newPred))

    diffImage = np.asarray(Image.new(mode="RGBA", size=(1024, 64), color=(255, 255, 255)))

    for x in range(np.shape(gtImg)[0]):
        for y in range(np.shape(gtImg)[1]):

            if ((not np.array_equal(expectedImg[x][y], newImg[x][y])) and
                (not np.array_equal(newImg[x][y], gtImg[x][y]))):
                unlabeled = (gtImg[x][y][0] == 220 and 
                        gtImg[x][y][1] == 220 and 
                        gtImg[x][y][2] == 220)
                outlier = (gtImg[x][y][0] == 0 and 
                        gtImg[x][y][1] == 0 and 
                        gtImg[x][y][2] == 0)
                if (not outlier or unlabeled):
                    diffImage[x][y] = newImg[x][y]

    return diffImage



def handleOne(mutation, mutationId, mutationRepo):
    global dedup
    global finalVisDir
    global dataDir
    global labelsDir
    global toolDir
    global predDir

    if (mutationId in dedup):
        return

    # Add the id to dedup in case models have duplicate top mutations 
    dedup.add(mutationId)

    """
    /finalvis
        /mutation
            /mutationId
                og-id : original scan with original labels
                new-id : new scan with new labels
                og-model-id : original scan with model labels (x3)
                og-model-asset-id : original asset scan with model labels (x3)
                new-model-id : new scan with model labels (x3)
    """

    print("Saving {} {}".format(mutation, mutationId))

    # Get the mutation data
    item = mutationRepo.getMutationDetailsById(mutationId)

    # Validate we have the details
    if (item == None):
        print("Details {} not found".format(mutationId))
        return

    # imageList = []
    imgs = []
    font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSansBold.ttf", 16)
    

    
    saveDir = finalVisDir + "/" + mutation + "/" + mutationId

    imgBuffer = Image.new(mode="RGBA", size=(1024, 20), color=(255, 255, 255))
    drawBuff = ImageDraw.Draw(imgBuffer)
    textBuff = "Id {}, Seq {}, Scene {}, AssetId {}".format(mutationId, item["baseSequence"], item["baseScene"], item["asset"])
    drawBuff.text((0, 0), textBuff, (0, 0, 0), font=font)
    imgs.append(np.asarray(imgBuffer))

    
    # Intensity Version
    scan.setIntensityColorType(True)

    # og-id : original scan with original labels
    origScanIntensity = saveDir + "/actual-og-intensity-" + mutationId + ".png"
    vis.set_new_pcd(scan_name=dataDir + "/" + item["baseSequence"] + "/velodyne/" + item["baseScene"] + ".bin",
                    label_name=labelsDir + "/" + item["baseSequence"] + "/labels/" + item["baseScene"] + ".label")
    vis.save(origScanIntensity)

    # new-id : new scan with new labels
    newScanIntensity = saveDir + "/actual-new-intensity" + mutationId + ".png"
    vis.set_new_pcd(scan_name=toolDir + "/done/velodyne/" + mutationId + ".bin",
                    label_name=toolDir + "/done/labels/" + mutationId + ".label")
    vis.save(newScanIntensity)

    ogImageIntensity = Image.open(origScanIntensity)
    newImageIntensity = Image.open(newScanIntensity)
    drawOgIntensity = ImageDraw.Draw(ogImageIntensity)
    drawNewIntensity = ImageDraw.Draw(newImageIntensity)
    drawOgIntensity.text((0, 0), "Orig Int", (255,255,255), font=font)
    drawNewIntensity.text((0, 0), "New Int", (255,255,255), font=font)
    imgs.append(np.asarray(ogImageIntensity))
    imgs.append(np.asarray(newImageIntensity))

    # Semanitc version 
    scan.setIntensityColorType(False)

    # og-id : original scan with original labels
    origScan = saveDir + "/actual-og-" + mutationId + ".png"
    vis.set_new_pcd(scan_name=dataDir + "/" + item["baseSequence"] + "/velodyne/" + item["baseScene"] + ".bin",
                    label_name=labelsDir + "/" + item["baseSequence"] + "/labels/" + item["baseScene"] + ".label")
    vis.save(origScan)

    # new-id : new scan with new labels
    newScan = saveDir + "/actual-new-" + mutationId + ".png"
    vis.set_new_pcd(scan_name=toolDir + "/done/velodyne/" + mutationId + ".bin",
                    label_name=toolDir + "/done/labels/" + mutationId + ".label")
    vis.save(newScan)

    ogImage = Image.open(origScan)
    newImage = Image.open(newScan)
    drawOg = ImageDraw.Draw(ogImage)
    drawNew = ImageDraw.Draw(newImage)
    drawOg.text((0, 0), "Orig Sem", (255,255,255), font=font)
    drawNew.text((0, 0), "New Sem", (255,255,255), font=font)
    imgs.append(np.asarray(ogImage))
    imgs.append(np.asarray(newImage))

    
    for model in models:

        imgBuffer = Image.new(mode="RGBA", size=(1024, 20), color=(255, 255, 255))
        drawBuff = ImageDraw.Draw(imgBuffer)
        textBuff = "Model: {}, Acc Loss {:.2f}%, Jacc Loss {:.2f}%, Predictions:".format(model, item[model]["percentLossAcc"], item[model]["percentLossJac"])
        drawBuff.text((0, 0), textBuff, (0, 0, 0), font=font)
        imgs.append(np.asarray(imgBuffer))

        # Adds asset's full scan removed when we moved to modified predictions
        # if "ADD" in mutation:
        #     # og-model-asset-id : original asset scan with model labels (x3)
        #     ogModelAssetSave = saveDir + model + "-asset-" + mutationId + ".png"
        #     vis.set_new_pcd(scan_name=dataDir + item["assetSequence"] + "/velodyne/" + item["assetScene"] + ".bin",
        #                 label_name=labelsDir + item["assetSequence"] + "/" + model + "/" + item["assetScene"] + ".label")
        #     vis.save(ogModelAssetSave)

        #     assetModelImage = Image.open(ogModelAssetSave)
        #     drawAsset = ImageDraw.Draw(assetModelImage)
        #     drawAsset.text((0, 0), "Asset " + model, (255,255,255), font=font)
        #     imgs.append(np.asarray(assetModelImage))


        # og-model-id : original scan with model labels (x3)
        ogModelSave = saveDir + "/" + model + "-og-" + mutationId + ".png"
        vis.set_new_pcd(scan_name=dataDir + "/" + item["baseSequence"] + "/velodyne/" + item["baseScene"] + ".bin",
                        label_name=predDir + "/" + item["baseSequence"] + "/" + model + "/" + item["baseScene"] + ".label")
        vis.save(ogModelSave)

        ogModelImage = Image.open(ogModelSave)
        drawOg = ImageDraw.Draw(ogModelImage)
        drawOg.text((0, 0), "Orig", (255,255,255), font=font)
        imgs.append(np.asarray(ogModelImage))


        ogModelModPredSave = ogModelSave
        if "INTENSITY" not in mutation and "DEFORM" not in mutation:
            # The assets modified prediction
            # og-model-modpred-id : mutated pred (x3)
            ogModelModPredSave = saveDir + "/" + model + "-modpred-" + mutationId + ".png"
            vis.set_new_pcd(scan_name=toolDir + "/done/velodyne/" + mutationId + ".bin",
                            label_name=toolDir + "/done/mutatedPred/" + model + "/" + mutationId + ".label")
            vis.save(ogModelModPredSave)

            modelModPredImage = Image.open(ogModelModPredSave)
            drawAsset = ImageDraw.Draw(modelModPredImage)
            drawAsset.text((0, 0), "Adj", (255,255,255), font=font)
            imgs.append(np.asarray(modelModPredImage))



        # new-model-id : new scan with model labels (x3)
        newModelSave = saveDir + "/" + model + "-new-" + mutationId + ".png"
        vis.set_new_pcd(scan_name=toolDir + "/done/velodyne/" + mutationId + ".bin",
                        label_name=toolDir + "/done/pred/" + model + "/" + mutationId + ".label")
        vis.save(newModelSave)
        
        newModelImage = Image.open(newModelSave)        
        drawNew = ImageDraw.Draw(newModelImage)        
        drawNew.text((0, 0), "New", (255,255,255), font=font)
        imgs.append(np.asarray(newModelImage))


        diffImg = getDiffImage(newScan, ogModelModPredSave, newModelSave)
        imgs.append(diffImg)



    # Combine into one image
    # https://stackoverflow.com/questions/30227466/combine-several-images-horizontally-with-python
    combineSave = finalVisDir + "/" + mutation + "/" + mutationId + ".png"
    imgsComb = np.vstack( imgs )
    imgsComb = Image.fromarray(imgsComb)
    imgsComb.save(combineSave)

       



def createImages(finalData, mutationRepo):
    global mutations
    global models

    for mutation in mutations:
        for model in models:
            for key in finalData[model][mutation].keys():
                if ("top" in key):
                    for mutationId in finalData[model][mutation][key]:
                        handleOne(mutation, mutationId[0], mutationRepo)



def parse_args():
    p = argparse.ArgumentParser(
        description='Model Runner')
    p.add_argument("-binPath", 
        help="Path to the semanticKITTI sequences", 
        nargs='?', const="",
        default="")
    p.add_argument("-labelPath", 
        help="Path to the ground truth label files", 
        nargs='?', const="",
        default="")
    p.add_argument("-predPath", 
        help="Path to the ground truth label files", 
        nargs='?', const="",
        default="")
    p.add_argument("-toolOutputPath", 
        help="Path to the data directory produced by the tool", 
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
    
    return p.parse_args()

    


# ----------------------------------------------------------

def main():
    global dataDir
    global labelsDir
    global predDir
    global toolDir
    global scan
    global vis
    global models

    print("\n\n------------------------------")
    print("\n\nStarting Range Image Conversion\n\n")

    args = parse_args() 
    dataDir = os.path.normpath(args.binPath)
    labelsDir = os.path.normpath(args.labelPath)
    predDir = os.path.normpath(args.predPath)
    toolDir = os.path.normpath(args.toolOutputPath)
    
    mutationRepo = DetailsRepository(args.mdb)

    finalData = {}
    with open(toolDir + "/finalData.json") as f:
        finalData = json.load(f)
    
    models = finalData["models"]

    setUpSaveDir(finalData, args.saveAt)

    # Set up visualization
    color_dict = color_map_alt_bgr
    nclasses = len(color_dict)
    scan = SemLaserScan(nclasses, color_dict, project=True)
    vis = LaserScanVis(scan=scan,
                    scan_name=dataDir + "/00/velodyne/000000.bin",
                    label_name=labelsDir + "/00/labels/000000.label")

    createImages(finalData, mutationRepo)


if __name__ == '__main__':
    main()



