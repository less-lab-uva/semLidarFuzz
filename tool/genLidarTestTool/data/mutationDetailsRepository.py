"""
DetailsRepository 
Handles all database interaction for mutation details

@Date 6/23/22
"""

import pymongo

import data.mongoRepository as mongoRepository

# --------------------------------------------------------------------------

class DetailsRepository(mongoRepository.MongoRepository):
    def __init__(self, mongoConnectPath):
        super(DetailsRepository, self).__init__(mongoConnectPath)
        self.mutationCollection = self.db["mutations"]
        

    """
    Get mutation details by id
    """
    def getMutationDetailsById(self, id):
        details = self.mutationCollection.find_one({"_id": id})

        return details

    """
    Save mutation data (Bulk)
    """
    def saveMutationDetails(self, mutationDetails):
        print("Saving {} Mutation Details".format(len(mutationDetails)))
        self.mutationCollection.insert_many(mutationDetails)


    """
    Page Request for mutation details
    Sorted first by time then on _id (in cases there are any duplicate times)
    
    https://github.com/nodebe/books_api/blob/main/books_api/books.py
    https://stackoverflow.com/questions/8109122/how-to-sort-mongodb-with-pymongo
    """
    def getMutationDetailsPaged(self, batchId, page, pageLimit):
        return self.mutationCollection.find({"batchId": batchId}).sort([("time", pymongo.ASCENDING), ("_id", pymongo.ASCENDING)]).skip((page - 1) * pageLimit).limit(pageLimit)

    """
    Count the details that have a given batchId
    """
    def countMutationDetailsBatchId(self, batchId):
        return self.mutationCollection.count_documents({"batchId": batchId})



