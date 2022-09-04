#!/bin/bash


# -------------------------------------------------------------------------------------------------------------------

# Options

# Where the final data json will come from
# Directory that contains the final output
toolData=""
# batch id to process
batchId=""

mongoconnect=$MONGO_CONNECT

# -------------------------------------------------------------------------------------------------------------------

# Run command
python produceCsv.py -id "$batchId" -mdb "$mongoconnect"

# -------------------------------------------------------------------------------------------------------------------




