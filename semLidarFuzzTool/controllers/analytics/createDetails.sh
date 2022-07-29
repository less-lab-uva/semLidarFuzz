#!/bin/bash


# -------------------------------------------------------------------------------------------------------------------

# Options

batchId="B9uvFtRe3BRe4FtPeDgzjT"

mongoconnect="/home/garrett/Documents/lidarTest2/mongoconnect.txt"
saveAt="/home/garrett/Documents/lidarTest2/toolV5/controllers/analytics"

# -------------------------------------------------------------------------------------------------------------------

# Run command 

python recreateFinalData.py -batchId "$batchId" -mdb "$mongoconnect" -saveAt $saveAt

# -------------------------------------------------------------------------------------------------------------------




