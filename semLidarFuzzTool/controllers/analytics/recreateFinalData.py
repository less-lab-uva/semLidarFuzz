"""
recreateFinalData
Recreates the final data for a given run

@Date 6/30/22
"""

import argparse
import os
import json

from data.mutationDetailsRepository import DetailsRepository
from service.eval.finalDetails import FinalDetails


# -------------------------------------------------------------

PAGE_LIMIT = 1000

# -------------------------------------------------------------


def recreate(detailsRepo, batchId, saveAt):

    finalDetails = FinalDetails(batchId)

    page = 0
    parsed = 0

    total = detailsRepo.countMutationDetailsBatchId(batchId)
    print("Total count for batchId {} is {}".format(batchId, total))

    # Parse the details in the batch
    while (parsed < total):
        page += 1
        print("Parsing details on page {} of size {}".format(page, PAGE_LIMIT))
        detailsCursor = detailsRepo.getMutationDetailsPaged(batchId, page, PAGE_LIMIT)

        detailsList = list(detailsCursor)
        count = len(detailsList)
        parsed += count
        print("Found {} on page {}, {}/{}".format(count, page, parsed, total))
        finalDetails.updateFinalDetails(detailsList)

        # Catch in case there was an error
        if (count == 0):
            total = total

    # Finalize averages ect
    finalDetails.finalizeFinalDetails()

    # Save the recreated final data
    with open(saveAt + '/finalData.json', 'w') as outfile:
        json.dump(finalDetails.finalData, outfile, indent=4, sort_keys=True)




def parse_args():
    p = argparse.ArgumentParser(
        description='Model Runner')

    p.add_argument("-mdb", 
        help="Path to the connection string for mongo", 
        nargs='?', const="/home/garrett/Documents/lidarTest2/mongoconnect.txt", 
        default="/home/garrett/Documents/lidarTest2/mongoconnect.txt")

    # Tool configurable params
    p.add_argument("-saveAt", 
        help="Location to save the tool output", 
        nargs='?', const=os.getcwd(), 
        default=os.getcwd())

    # Recreation options
    p.add_argument("-batchId", 
        help="Batch Id to rerun", 
        default="",
        required=True)
    
    return p.parse_args()


# ----------------------------------------------------------

def main():

    print("\n\n------------------------------")
    print("\n\nStarting Final Data Recreation\n\n")
    
    # Get arguments 
    args = parse_args()
    
    saveAt = args.saveAt
    batchId = args.batchId
    mongoConnect = args.mdb

    # DB
    detailsRepo = DetailsRepository(mongoConnect)

    # Recreate the final data
    recreate(detailsRepo, batchId, saveAt)




   


if __name__ == '__main__':
    main()



