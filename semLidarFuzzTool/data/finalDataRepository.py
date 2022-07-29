"""
FinalDataRepository 
Handles all database interaction for final data

@Date 6/23/22
"""

from pymongo import MongoClient

import data.mongoRepository as mongoRepository

# --------------------------------------------------------------------------


class FinalDataRepository(mongoRepository.MongoRepository):
    def __init__(self, mongoConnectPath):
        super(FinalDataRepository, self).__init__(mongoConnectPath)
        self.finalDataCollection = self.db["final_data"]    
        

    """
    Get final data by id
    """
    def getFinalDataById(self, id):
        data = self.finalDataCollection.find_one({"_id": id})

        return data


    """
    Save final data
    """
    def saveFinalData(self, finalData):
        self.finalDataCollection.insert_one(finalData)



