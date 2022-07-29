"""
MongoRepository 
Base class that connects to mongo client
Inherited by other repository classes

@Date 6/23/22
"""

from pymongo import MongoClient

# --------------------------------------------------------------------------


class MongoRepository:
    def __init__(self, mongoConnectPath):
        self.db = self.mongoConnect(mongoConnectPath)

    """
    Connect to mongodb 
    """
    def mongoConnect(self, mongoConnectPath):

        configFile = open(mongoConnectPath, "r")
        mongoUrl = configFile.readline()
        configFile.close()
        
        client = MongoClient(mongoUrl)
        return client["lidar_data"]




