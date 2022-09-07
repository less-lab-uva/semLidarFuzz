#!/bin/bash

# -------------------------------------------------------------------------------------------------------------------



saveDir=$SAVE_DIR
mkdir $saveDir

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
    binPath=$BIN_PATH
    # Labels for those scans
    lblPath=$LABEL_PATH
    # Models original predictions on those scans
    predPath=$PRED_PATH
    # Full path to the mongo connect
    mongoconnect=$MONGO_CONNECT
    # Path to model directory
    modelDir=$MODEL_DIR

    # Models to use for the run comma seperated
    models=$MODELS
    # Total count of total mutations to generate 
    count=50000
    # How often evaluation will trigger
    batch=50000

    # Run command 
    cd controllers/mutationTool
    if [ "$mutation" = "ADD_ROTATE" ] || [ "$mutation" = "ADD_MIRROR_ROTATE" ] ; then
      python genLidarTests.py -binPath "$binPath" -labelPath $lblPath -predPath $predPath -mdb $mongoconnect -modelDir $modelDir -mutation $mutation -count $count -batch $batch -saveAt $newSaveDir -models $models -threadCount 1
    else
      python genLidarTests.py -binPath "$binPath" -labelPath $lblPath -predPath $predPath -mdb $mongoconnect -modelDir $modelDir -mutation $mutation -count $count -batch $batch -saveAt $newSaveDir -models $models -threadCount 5
    fi
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





