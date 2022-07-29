
import csv
import argparse
import json
import os
import sys
from itertools import combinations

import data.finalDataRepository as finalDataRepository
import domain.mutationsEnum as mutationsEnum

# --------------------------------------------------------------------------------

models = []
modelCombos = []

# --------------------------------------------------------------------------------

def creatBucketCol(bucketData, bucketKey):
    
    col = [bucketKey]
    col.append(bucketData["total"])
    for model in models:
        col.append(bucketData["total_" + model])

    col.append("")
    col.append("")
    for modelCombo in modelCombos:
        if (modelCombo in bucketData["model_overlap"].keys()):
            col.append(bucketData["model_overlap"][modelCombo])
        else:
            col.append(0)

    col.append("")
    col.append("")
    for modelCombo in modelCombos:
        if (modelCombo in bucketData["model_threshold_overlap"].keys()):
            col.append(bucketData["model_threshold_overlap"][modelCombo])
        else:
            col.append(0)
        
    col.append("")

    col.append(bucketData["avg"]) 
    for model in models:
        col.append(bucketData["avg_" + model])

    if (bucketData["min"] == sys.maxsize):
        col.append("-")
    else:
        col.append(bucketData["min"])
    for model in models:
        if (bucketData["min_" + model] == sys.maxsize):
            col.append("-")
        else:
            col.append(bucketData["min_" + model])

    
    if (bucketData["max"] == sys.maxsize * -1):
        col.append("-")
    else:
        col.append(bucketData["max"])
    for model in models:
        if (bucketData["max_" + model] == sys.maxsize * -1):
            col.append("-")
        else:
            col.append(bucketData["max_" + model])
    
    col.append("")

    if (bucketData["min_points_affected"] == sys.maxsize):
        col.append("-")
    else:
        col.append(bucketData["min_points_affected"])
    if (bucketData["max_points_affected"] == sys.maxsize * -1):
        col.append("-")
    else:
        col.append(bucketData["max_points_affected"])
    col.append(bucketData["avg_points_affected"])

    col.append("")

    if (bucketData["min_seconds"] == sys.maxsize):
        col.append("-")
    else:
        col.append(bucketData["min_seconds"])
    if (bucketData["max_seconds"] == sys.maxsize * -1):
        col.append("-")
    else:
        col.append(bucketData["max_seconds"])
    col.append(bucketData["avg_seconds"])

    col.append("")

    col.append("")
    col.append("")

    col.append("")
    col.append("")

    col.append("")
    col.append("")



    return col

def creatAllCol(allData, duplicates, duplicatePercent, time):
    
    col = ["All"]
    col.append(allData["total"] * len(models))
    for _ in models:
        col.append(allData["total"])
    
    # overlap
    col.append("")
    col.append("")
    for _ in modelCombos:
        col.append("")

    # overlap threshold
    col.append("")
    col.append("")
    for _ in modelCombos:
        col.append("")
            
    col.append("")

    col.append(allData["avg"])
    for model in models:
        col.append(allData["avg_" + model])

    col.append(allData["min"])
    for model in models:
        col.append(allData["min_" + model])

    col.append(allData["max"])
    for model in models:
        col.append(allData["max_" + model])

    col.append("")

    col.append(allData["min_points_affected"])
    col.append(allData["max_points_affected"])
    col.append(allData["avg_points_affected"])

    col.append("")

    col.append(allData["min_seconds"])
    col.append(allData["max_seconds"])
    col.append(allData["avg_seconds"])

    col.append("")

    col.append(duplicates)
    col.append(duplicatePercent)

    col.append("")

    col.append(time)

    col.append("")



    return col

def createMutationCsv(mutationDataAcc, mutation, accType, saveAt, bucketKeys, time):

    print("Creating csv for {} {}".format(mutation, accType))

    mutationData = mutationDataAcc[accType]

    cols = []

    titleCol = [mutation, "Total"]
    for model in models:
        titleCol.append(model + " Total")

    titleCol.append("")
    titleCol.append("Bucket Overlap")
    for modelCombo in modelCombos:
        titleCol.append(modelCombo)

    titleCol.append("")
    titleCol.append("Failure Thresholds")
    for modelCombo in modelCombos:
        titleCol.append(modelCombo)
        
    titleCol.append("")

    titleCol.append("Avg " + accType + " % Loss") 
    for model in models:
        titleCol.append("Avg " + accType + " % Loss {}".format(model))

    titleCol.append("Min " + accType + " % Loss")
    for model in models:
        titleCol.append("Min " + accType + " % Loss {}".format(model))

    titleCol.append("Max " + accType + " % Loss")
    for model in models:
        titleCol.append("Max " + accType + " % Loss {}".format(model))

    titleCol.append("")

    titleCol.append("Min Points Affected")
    titleCol.append("Max Points Affected")
    titleCol.append("Avg Points Affected")

    titleCol.append("")

    titleCol.append("Min Seconds")
    titleCol.append("Max Seconds")
    titleCol.append("Avg Seconds")

    titleCol.append("")

    titleCol.append("Duplicates")
    titleCol.append("Duplicates Percent")

    titleCol.append("")

    titleCol.append("Time")

    titleCol.append("")
    

    
    cols.append(titleCol)

    allCol = creatAllCol(mutationData["all"], mutationDataAcc["duplicates"], mutationDataAcc["duplicatesPercent"], time)
    cols.append(allCol)


    for bucketKey in bucketKeys:
        bucketCol = creatBucketCol(mutationData[bucketKey], bucketKey)
        cols.append(bucketCol)

    cols.append([""] * len(allCol))

    keyCol = ["", "Key", 
            "bucket_0:         x >= -0.1%", 
            "bucket_1: -0.1% > x >= -1%", 
            "bucket_2:   -1% > x >= -2%", 
            "bucket_3:   -2% > x >= -3%",
            "bucket_4:   -3% > x >= -4%",
            "bucket_5:   -4% > x >= -5%",
            "bucket_6:   -5% > x"]
    while (len(keyCol) < len(allCol)):
        keyCol.append("")
    cols.append(keyCol)
     
    rows = zip(*cols)

    csvFileName = saveAt + "/" + mutation + "_" + accType + ".csv"
    print("Saving csv at {}".format(csvFileName))
    csvFile = open(csvFileName, "w")
    csvWriter = csv.writer(csvFile)

    for row in rows:
        csvWriter.writerow(row)


def getModelComboKeys():

    combos = []
    for n in range(1, len(models) + 1):
        combos += list(combinations(models, n))

    comboKeys = []
    for combo in combos:
        comboKeys.append("_".join(combo))

    return comboKeys


def parse_args():
    p = argparse.ArgumentParser(
        description='Model Runner')
    p.add_argument("-data", 
        help="Path to the data directory produced by the tool", 
        nargs='?', const="/home/garrett/Documents/lidarTest2/toolV5/data/", 
        default="/home/garrett/Documents/lidarTest2/toolV5/data/")
    p.add_argument("-id", 
        help="Id to the final data to create the report for", 
        nargs='?', const=None, default=None)
    p.add_argument("-mdb", 
        help="Path to the mongo connect file", 
        nargs='?', const="/home/garrett/Documents/lidarTest2/mongoconnect.txt", 
        default="/home/garrett/Documents/lidarTest2/mongoconnect.txt")
    p.add_argument("-saveAt", 
        help="Where to save the mutation results", 
        nargs='?', const=os.getcwd(), 
        default=os.getcwd())
    
    return p.parse_args()

    
# ----------------------------------------------------------

def main():
    global modelCombos
    global models

    print("\n\n------------------------------")
    print("\n\nStarting Mutation CSV Generator\n\n")

    args = parse_args() 
    dataDir = args.data
    dataId = args.id
    data = None

    # Get the final data json
    # Get from database if id is provided
    if (dataId != None):
        print("Getting data from mongo with id {}".format(dataId))
        finalDataRepo = finalDataRepository.FinalDataRepository(args.mdb)
        data = finalDataRepo.getFinalDataById(dataId)

    # Get from the output directory
    if (data == None):
        print("Getting data from {}".format(dataDir + 'finalData.json'))
        # Opening JSON file
        f = open(dataDir + 'finalData.json')
        # returns JSON object as a dictionary
        data = json.load(f)
    print("Final Data Keys: {}".format(data.keys()))

    # Get mutation keys and bucket keys 
    mutations = data["mutations"]
    bucketKeys = data["buckets"]
    models = data["models"]
    modelCombos = getModelComboKeys()

    # Create a csv with the data from the final data json run 
    for mutationKey in mutations:
        createMutationCsv(data[mutationKey], mutationKey, "accuracy", args.saveAt, bucketKeys, data["time"])
        createMutationCsv(data[mutationKey], mutationKey, "jaccard", args.saveAt, bucketKeys, data["time"])
    
    


if __name__ == '__main__':
    main()



