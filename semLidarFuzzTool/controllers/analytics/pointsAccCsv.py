
import csv
import argparse
import json
import os

from data.mutationDetailsRepository import DetailsRepository

# --------------------------------------------------------------------------------

PAGE_LIMIT = 1000

"""
Creates a csv for the acc point time analysis
"""
def getAccPointTimeCsv(batchId, mongoConnect, saveAt):
    print("Recreating batch {}".format(batchId))

    # Connect to collections
    detailsRepository = DetailsRepository(mongoConnect)

    csvFile = None
    csvWriter = None

    page = 0
    parsed = 0
    
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
        if page == 1:
            csvFileName = saveAt + "/" + detailsList[0]["mutation"] + "-accPointTime.csv"
            print("Saving csv at {}".format(csvFileName))
            csvFile = open(csvFileName, "w")
            csvWriter = csv.writer(csvFile)
            csvWriter.writerow([detailsList[0]["mutation"], "", "", "", "", "", "", ""])
            csvWriter.writerow(["Acc % Loss Cyl", "Jacc % Loss Cyl", "Acc % Loss Spv", "Jacc % Loss Spv", "Acc % Loss Sal", "Jacc % Loss Sal", "Points", "Seconds"])
        
        for details in detailsList:
            row = []
            for model in ["cyl", "spv", "sal"]:
                row.append(details[model]["percentLossAcc"])
            for model in ["cyl", "spv", "sal"]:
                row.append(details[model]["percentLossJac"])
            row.append(details["pointsAffected"])
            row.append(details["seconds"])
            csvWriter.writerow(row)

        # Catch in case there was an error
        if (count == 0):
            total = parsed



    

def parse_args():
    p = argparse.ArgumentParser(
        description='Model Runner')
    p.add_argument("-batchId", 
        help="Id for the batch", 
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

    print("\n\n------------------------------")
    print("\n\nStarting Mutation CSV Generator\n\n")

    args = parse_args() 

    
    getAccPointTimeCsv(args.batchId, args.mdb, args.saveAt)
    


if __name__ == '__main__':
    main()



