"""
modelEvaluationInitial
Get the original accuracy and jaccard values for the base model predictions

@Date 6/30/22
"""


from pymongo import MongoClient
import glob, os
import numpy as np
import open3d as o3d
import sys
from os.path import basename
import argparse

from service.eval.ioueval import iouEval
from domain.semanticMapping import name_label_mapping
from domain.semanticMapping import learning_map
from domain.semanticMapping import learning_map_inv
from domain.semanticMapping import learning_ignore


# -------------------------------------------------------------


def getPointMetrics(label_file):

    # +100 hack making lut bigger just in case there are unknown labels
    maxkey = max(learning_map.keys())
    remap_lut = np.zeros((maxkey + 100), dtype=np.int32)
    remap_lut[list(learning_map.keys())] = list(learning_map.values())

    # Label
    label = np.fromfile(label_file, dtype=np.int32)
    label = label.reshape((-1))  # reshape to vector
    label = label & 0xFFFF       # get lower half for semantics


    label = remap_lut[label] # remap to xentropy format

    pointCount = len(label)
    pointMetrics = {}

    for learningNum in learning_map_inv.keys():
        pointsForClass = np.sum(label == learningNum)
        className = name_label_mapping[learning_map_inv[learningNum]]
        pointMetrics[className] = int(pointsForClass)

    return pointCount, pointMetrics



# https://github.com/PRBonn/semantic-kitti-api/blob/master/evaluate_semantics.py
def eval(label_file, pred_file):

    print()
    print(label_file)
    print(pred_file)


    numClasses = len(learning_map_inv)

    # make lookup table for mapping
    maxkey = max(learning_map.keys())

    # +100 hack making lut bigger just in case there are unknown labels
    remap_lut = np.zeros((maxkey + 100), dtype=np.int32)
    remap_lut[list(learning_map.keys())] = list(learning_map.values())

    # create evaluator
    ignore = []
    for cl, ign in learning_ignore.items():
        if ign:
            x_cl = int(cl)
            ignore.append(x_cl)
            print("Ignoring xentropy class ", x_cl, " in IoU evaluation")

    evaluator = iouEval(numClasses, ignore)
    evaluator.reset()

    label = np.fromfile(label_file, dtype=np.int32)
    label = label.reshape((-1))  # reshape to vector
    label = label & 0xFFFF       # get lower half for semantics

    # open prediction
    pred = np.fromfile(pred_file, dtype=np.int32)
    pred = pred.reshape((-1))    # reshape to vector
    pred = pred & 0xFFFF         # get lower half for semantics

    label = remap_lut[label] # remap to xentropy format
    pred = remap_lut[pred] # remap to xentropy format

    # add single scan to evaluation
    evaluator.addBatch(pred, label)

    # when I am done, print the evaluation
    m_accuracy = evaluator.getacc()
    # m_jaccard, m_jaccard_modified, class_jaccard = evaluator.getIoU()
    m_jaccard, class_jaccard = evaluator.getIoU()

    results = {}
    results["jaccard"] = m_jaccard.item()
    # results["jaccardAlt"] = m_jaccard_modified.item()
    results["accuracy"] = m_accuracy.item()

    # print also classwise
    for i, jacc in enumerate(class_jaccard):
        if i not in ignore:
            print('IoU class {i:} [{class_str:}] = {jacc:.3f}'.format(
            i=i, class_str=name_label_mapping[learning_map_inv[i]], jacc=jacc))

            results[name_label_mapping[learning_map_inv[i]]] = jacc

    # print for spreadsheet
    print("*" * 80)
    print("below can be copied straight for paper table")
    for i, jacc in enumerate(class_jaccard):
        if i not in ignore:
            sys.stdout.write('{jacc:.3f}'.format(jacc=jacc.item()))
            sys.stdout.write(",")
    sys.stdout.write('{jacc:.3f}'.format(jacc=m_jaccard.item()))
    sys.stdout.write(",")
    sys.stdout.write('{acc:.3f}'.format(acc=m_accuracy.item()))
    sys.stdout.write('\n')
    sys.stdout.flush()


    return results
    



"""
Connect to mongodb 
"""
def mongoConnect():
    configFile = open(os.environ['MONGO_CONNECT'], "r")
    mongoUrl = configFile.readline()
    configFile.close()
    
    client = MongoClient(mongoUrl)
    db = client["lidar_data"]
    return db


def parse_args():
    p = argparse.ArgumentParser(
        description='Model Runner')
    p.add_argument("-labels", 
        help="Path to the labels", 
        nargs='?', const="",
        default="")
    p.add_argument("-pred", 
        help="Path to the predictions made by the tools", 
        nargs='?', const="",
        default="")
    
    return p.parse_args()


def main():
    print("\n\n------------------------------")
    print("\n\nStarting Model Evaluation Upload\n\n")

    print("Connecting to Mongo")
    mdb = mongoConnect()
    mdbCol = mdb["base_accuracy3"]
    print("Connected")

    args = parse_args()
    models = ["cyl", "spv", "sal", "sq3", "pol", "js3c_gpu", "js3c_cpu"]
    labelBasePath = args.labels
    predBasePath = args.pred


    items = 0
    acc = {}
    iou = {}

    for model in models:
        acc[model] = 0
        iou[model] = 0
    
    for x in range(0, 11):

        add = []

        folderNum = str(x).rjust(2, '0')

        # Get pred label / pred path
        labelPath = labelBasePath + folderNum + "/labels/"
        predPaths = {}
        for model in models:
            predPaths[model] = predBasePath + folderNum + "/" + model + "/"

        # Get label / pred files sort
        labelFiles = glob.glob(labelPath + "*.label")
        labelFiles = sorted(labelFiles)  
        predFilesModel = {}
        for model in models:
            predFilesModel[model] = glob.glob(predPaths[model] + "*.label")
            predFilesModel[model] = sorted(predFilesModel[model])
        
        for index in range(0, len(labelFiles)):

            fileName = basename(labelFiles[index])
            fileName = fileName.replace(".label", "")

            sceneEval = {}
            sceneEval["_id"] = folderNum + "-" + fileName
            sceneEval["sequence"] = folderNum
            sceneEval["scene"] = fileName

            pointCounts, pointMetrics = getPointMetrics(labelFiles[index])
            sceneEval["points"] = pointCounts
            sceneEval["pointMetrics"] = pointMetrics

            for model in models:
                sceneEval[model] = eval(labelFiles[index], predFilesModel[model][index])
                acc[model] += sceneEval[model]["accuracy"]
                iou[model] += sceneEval[model]["jaccard"]

            items += 1

            add.append(sceneEval)

            print(pointCounts)
            print(pointMetrics)

        mdbCol.insert_many(add)


    print("\n\n\nDONE ACC JAC:\n")
    for model in models:
        print(model)
        print(acc[model] / items)
        print(iou[model] / items)
        


if __name__ == '__main__':
    main()

































