
import csv
import argparse
import json
import os
import sys
from pymongo import MongoClient

from data.mutationDetailsRepository import DetailsRepository
from domain.mutationsEnum import Mutation


# --------------------------------------------------------------------------------

PAGE_LIMIT = 1000


"""
batchRecreation
Get details by a batch Id then save
"""
def checkForDupsRemove(batchId, mongoConnect):
    print("Checking for dups in batch {}".format(batchId))

    # Connect to collections
    detailsRepository = DetailsRepository(mongoConnect)

    page = 0
    parsed = 0
    
    duplicates = set()

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
            if details["mutation"] == Mutation.ADD_ROTATE.name:
                duplicates.add((details["asset"], details["baseSequence"], details["baseScene"], details["rotate"]))
            elif details["mutation"] == Mutation.ADD_MIRROR_ROTATE.name:
                duplicates.add((details["asset"], details["baseSequence"], details["baseScene"], details["rotate"], details["mirror"]))
            elif details["mutation"] == Mutation.SCENE_REMOVE.name:
                duplicates.add((details["asset"]))
            elif details["mutation"] == Mutation.SIGN_REPLACE.name:
                duplicates.add((details["asset"], details["sign"]))
            elif details["mutation"] == Mutation.VEHICLE_SCALE.name:
                duplicates.add((details["asset"], details["scale"]))
            elif details["mutation"] == Mutation.VEHICLE_INTENSITY.name:
                duplicates.add((details["asset"], details["intensity"]))
            elif details["mutation"] == Mutation.VEHICLE_DEFORM.name:
                duplicates.add((details["asset"], details["deformPercent"], details["deformPoint"], details["deformMu"], details["deformSigma"], details["deformSeed"]))
            else:
                print("{} not a supported mutation".format(details["mutation"]))


    print("Total mutation count {}, found {} duplicates, {} unique for batch {}".format(total, total - len(duplicates), len(duplicates), batchId))
    print("{}%".format((total - len(duplicates)) / total))






def parse_args():
    p = argparse.ArgumentParser(
        description='Model Runner')
    p.add_argument("-id", 
        help="Id to the final data to create the report for", 
        nargs='?', const=None, default=None)
    p.add_argument("-mdb", 
        help="Path to the mongo connect file", 
        nargs='?', const="/home/garrett/Documents/lidarTest2/mongoconnect.txt", 
        default="/home/garrett/Documents/lidarTest2/mongoconnect.txt")
    
    return p.parse_args()

    
# ----------------------------------------------------------

def main():

    print("\n\n------------------------------")
    print("\n\nStarting Mutation Duplicate Checker\n\n")

    args = parse_args() 
    dataId = args.id

    if (dataId == None):
        print("Batch Id Required!")

    print("Getting data from mongo with id {}".format(dataId))

    checkForDupsRemove(dataId, args.mdb)

if __name__ == '__main__':
    main()



