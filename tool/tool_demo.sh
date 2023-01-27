# Move on to tool setup
export PYTHONPATH=/root/genLidarTestTool
export DISPLAY=":0"
export RUNNING_IN_DOCKER=gen_lidar_tests
export MONGO_CONNECT=/root/mongoconnect.txt
export MODEL_DIR=/root/genLidarTestTool/suts
export STAGING_DIR=/root/tmp/dataset/sequences/00/velodyne/
export PRED_PATH=/root/pred_data/
export LABEL_PATH=/root/selected_data/semantic_kitti_labels/dataset/sequences/
export BIN_PATH=/root/selected_data/semantic_kitti_pcs/dataset/sequences/
export MODELS="cyl,js3c_gpu,sal"
printf "Setting up Docker container\n"
docker-compose up --build -d
if test -f ".keep" ; then
  printf "One time setup has already been completed, skipping.\n"
else
  printf "Downloading selected data to use for generating tests\n"
  docker-compose exec gen_lidar_tests bash -c "mkdir /root/selected_data 2>/dev/null"
  docker-compose exec gen_lidar_tests bash -c "wget -O /root/selected_data.tar.xz https://zenodo.org/record/7569212/files/selected_data.tar.xz?download=1 && printf \"Extracting selected data to ./selected_data, this may take a moment\n\" && tar -xf /root/selected_data.tar.xz -C /root/selected_data --strip-components=1 --checkpoint=.250 && rm /root/selected_data.tar.xz" && \
  printf "\nPerforming Resource Collection\n" && \
  docker-compose exec gen_lidar_tests bash -c "python3 /root/genLidarTestTool/controllers/extractInstances/instanceExtractorV4.py -mdb /root/mongoconnect.txt -labelPath /root/selected_data/semantic_kitti_labels/dataset/sequences -binPath /root/selected_data/semantic_kitti_pcs/dataset/sequences" && \
  printf "Resource Collection Complete\n" && \
  touch .keep
fi
docker-compose exec gen_lidar_tests bash -c "mkdir $PRED_PATH 2>/dev/null"

printf "Setting up SUTs\n"
cd genLidarTestTool
mkdir suts 2>/dev/null
cd suts
# JS3C-Net
git clone https://github.com/less-lab-uva/JS3C-Net.git
cd JS3C-Net
git checkout 3b9dc85721c8609a55eb2f582860c9736c5c79ce
cd ..
# SalsaNext
git clone https://github.com/less-lab-uva/SalsaNext.git
cd SalsaNext
git checkout bd1308b02e05db982664fae2da04ee709cd14098
if test -f ".keep" ; then
  printf "Pretrained data already downloaded\n"
else
  docker-compose exec gen_lidar_tests bash -c "wget -O /root/genLidarTestTool/suts/SalsaNext/pretrained.tar.xz https://zenodo.org/record/7574602/files/pretrained.tar.xz?download=1 && printf \"Extracting training data to /root/genLidarTestTool/suts/SalsaNext/pretrained, this may take a moment\n\" && mkdir /root/genLidarTestTool/suts/SalsaNext/pretrained 2>/dev/null && tar -xf /root/genLidarTestTool/suts/SalsaNext/pretrained.tar.xz -C /root/genLidarTestTool/suts/SalsaNext/pretrained --strip-components=1 --checkpoint=.250 && rm /root/genLidarTestTool/suts/SalsaNext/pretrained.tar.xz" && \
  touch .keep
fi
cd ..
# Cylinder3D
git clone https://github.com/less-lab-uva/Cylinder3D.git
cd Cylinder3D
git checkout 89215b91aa57dda26ea3b89f0b43139750047ab2
cd ..
# SqueezeSegV3
git clone https://github.com/less-lab-uva/SqueezeSegV3.git
cd SqueezeSegV3
git checkout 543196b551ea370021533185b4527a326ce2fcf6
cd ..
cd ../..
export models=$MODELS

if test -f ".sut" ; then
  printf "SUT initial predictions have already been recorded\n"
else
  printf "Performing SUT initial predictions\n"
  docker-compose exec gen_lidar_tests bash -c "cd /root/genLidarTestTool/controllers/modelBasePred/ && source runBaseEval.sh" && \
  touch .sut
fi

# Total count of total mutations to generate
count=5
saveDir=/root/sample_tool_output
docker-compose exec gen_lidar_tests bash -c "cd /root/genLidarTestTool && source setup.sh"
printf "Generating $count mutations for each type and saving to ./sample_tool_output\n"
for mutation in "VEHICLE_INTENSITY" "ADD_ROTATE" "ADD_MIRROR_ROTATE" "SCENE_REMOVE" "SIGN_REPLACE" "VEHICLE_DEFORM" "VEHICLE_SCALE"
do
  current_time=$(date "+%Y_%m_%d-%H_%M_%S")
  newDir=$mutation"_"$current_time
  newSaveDir=$saveDir/$newDir
  outputDir="$newSaveDir/output/"
  printf "Generating $count mutations for $mutation, saving to ./sample_tool_output/$newDir\n"
  docker-compose exec gen_lidar_tests bash -c "mkdir $newSaveDir 2>/dev/null"
  docker-compose exec gen_lidar_tests bash -c "python3 /root/genLidarTestTool/controllers/mutationTool/genLidarTests.py -binPath /root/selected_data/semantic_kitti_pcs/dataset/sequences -labelPath /root/selected_data/semantic_kitti_labels/dataset/sequences -predPath $PRED_PATH -mdb /root/mongoconnect.txt -mutation $mutation -count $count -batch $count -saveAt $newSaveDir -modelDir $MODEL_DIR -models $MODELS -threadCount 1"
  docker-compose exec gen_lidar_tests bash -c "mv $newSaveDir/output/staging/* $newSaveDir/output/done/velodyne/ 2>/dev/null"
  printf "Generating visualizations\n"
  # the Xvfb parts are to account for the fact we are running in a container without proper display access
  docker-compose exec gen_lidar_tests bash -c "(pgrep -x Xvfb >/dev/null || Xvfb :0 -screen 0 1024x768x24 -ac +extension GLX +render -noreset &) && python3 /root/genLidarTestTool/controllers/finalVisualize/finalVisualization.py -binPath /root/selected_data/semantic_kitti_pcs/dataset/sequences -labelPath /root/selected_data/semantic_kitti_labels/dataset/sequences -mdb /root/mongoconnect.txt -saveAt $outputDir -toolOutputPath $outputDir -predPath $PRED_PATH -vis_all"
  printf "Generating SUT analytics\n"
  docker-compose exec gen_lidar_tests bash -c "python3 /root/genLidarTestTool/controllers/analytics/produceCsv.py -data \"$outputDir\" -mdb \"$MONGO_CONNECT\" -saveAt $outputDir"
done
docker-compose exec gen_lidar_tests bash -c "rm -rf /root/.nv 2>/dev/null" 2>/dev/null