#!/bin/bash

# -------------------------------------------------------------------------------------------------------------------



saveDir="/home/garrett/tmp/jsc3test"


# "ADD_ROTATE" "ADD_MIRROR_ROTATE" "SCENE_REMOVE" "SIGN_REPLACE" "VEHICLE_DEFORM" "VEHICLE_INTENSITY" "VEHICLE_SCALE"
# for mutation in "VEHICLE_INTENSITY"
for mutation in "VEHICLE_INTENSITY" "ADD_ROTATE" "ADD_MIRROR_ROTATE" "SCENE_REMOVE" "SIGN_REPLACE" "VEHICLE_DEFORM" "VEHICLE_SCALE"
do
# -------------------------------------------------------------------------------------------------------------------


    echo "Running Tool"


    echo "Mutation: $mutation"

    current_time=$(date "+%Y_%m_%d-%H_%M_%S")
    echo "Current Time: $current_time"
    
    newDir=$mutation"_"$current_time
    echo "Dir name: $newDir"

    newSaveDir=$saveDir/$newDir
    echo "Save at: $newSaveDir"

    mkdir $newSaveDir

    outputDir="$newSaveDir/output/"
    echo "Output will be at: $outputDir"


    # -------------------------------------------------------------------------------------------------------------------

    echo "Running Mutation Generation & Evaluation"

    # Original scans
    binPath="/home/garrett/Documents/data/dataset/sequences/"
    # Labels for those scans
    lblPath="/home/garrett/Documents/data/dataset4/sequences/"
    # Models original predictions on those scans
    predPath="/home/garrett/Documents/data/resultsBase/"
    # Full path to the mongo connect
    mongoconnect="/home/garrett/Documents/lidarTest2/mongoconnect.txt"
    # Path to model directory
    modelDir="/home/garrett/Documents"

    # Models to use for the run comma seperated
    models="cyl,spv,js3c_gpu,sal,sq3,pol"
    # Total count of total mutations to generate 
    count=50000
    # How often evaluation will trigger
    batch=1000

    # Run command 
    cd controllers/mutationTool
    python semFuzzLidar.py -binPath "$binPath" -labelPath $lblPath -predPath $predPath -mdb $mongoconnect -modelDir $modelDir -mutation $mutation -count $count -batch $batch -saveAt $newSaveDir -models $models
    cd ../..

    # -------------------------------------------------------------------------------------------------------------------s

    echo "Running Visulization"


    cd controllers/finalVisualize
    python finalVisualization.py -binPath "$binPath" -labelPath "$lblPath" -predPath $predPath -toolOutputPath "$outputDir" -mdb "$mongoconnect" -saveAt $outputDir
    cd ../..

    # -------------------------------------------------------------------------------------------------------------------

    echo "Running Analytics"


    cd controllers/analytics
    python produceCsv.py -data "$outputDir" -mdb "$mongoconnect" -saveAt $outputDir
    cd ../..


done





