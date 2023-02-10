if test -f ".docker" ; then
  printf "One time Docker image download has already been completed, skipping.\n"
else
  printf "Downloading pre-build Docker images from Zenodo. This download is ~2.5GB and may take quite a while.\n"
  printf "You may instead build the Docker image locally using ./build_docker.sh, which may be much faster.\n"
  curl https://zenodo.org/record/7627337/files/gen_lidar_tests.docker.tar.gz?download=1 | docker load && \
  curl https://zenodo.org/record/7627337/files/lidar_tests_mongo.docker.tar.gz?download=1 | docker load && \
  touch .docker
fi
export PYTHONPATH=/root/genLidarTestTool
export DISPLAY=":0"
export RUNNING_IN_DOCKER=gen_lidar_tests
export MONGO_CONNECT=/root/mongoconnect.txt
export MODEL_DIR=/root/genLidarTestTool/suts
export STAGING_DIR=/root/tmp/dataset/sequences/00/velodyne/
export PRED_PATH=/root/pred_data/
export LABEL_PATH=/root/selected_data/semantic_kitti_labels/dataset/sequences/
export BIN_PATH=/root/selected_data/semantic_kitti_pcs/dataset/sequences/
printf "Setting up Docker container\n"
docker-compose up --build -d
if test -f ".keep" ; then
  printf "One time setup has already been completed, skipping.\n"
else
  printf "Downloading selected data to use for generating tests\n"
  docker-compose exec gen_lidar_tests bash -c "mkdir /root/selected_data 2>/dev/null"
  docker-compose exec gen_lidar_tests bash -c "wget -O /root/selected_data.tar.xz https://zenodo.org/record/7569212/files/study_data_compressed.tar.xz?download=1 && printf \"Extracting selected data to ./selected_data, this may take a moment\n\" && tar -xf /root/selected_data.tar.xz -C /root/selected_data --strip-components=1 --checkpoint=.250 && rm /root/selected_data.tar.xz" && \
  printf "\nPerforming Resource Collection\n" && \
  docker-compose exec gen_lidar_tests bash -c "python3 /root/genLidarTestTool/controllers/extractInstances/instanceExtractorV4.py -mdb /root/mongoconnect.txt -labelPath /root/selected_data/semantic_kitti_labels/dataset/sequences -binPath /root/selected_data/semantic_kitti_pcs/dataset/sequences" && \
  printf "Resource Collection Complete\n" && \
  touch .keep
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
  docker-compose exec gen_lidar_tests bash -c "python3 /root/genLidarTestTool/controllers/mutationTool/genLidarTests.py -binPath /root/selected_data/semantic_kitti_pcs/dataset/sequences -labelPath /root/selected_data/semantic_kitti_labels/dataset/sequences -mdb /root/mongoconnect.txt -mutation $mutation -count $count -batch $count -saveAt $newSaveDir -threadCount 1 -ne"
  docker-compose exec gen_lidar_tests bash -c "mv $newSaveDir/output/staging/* $newSaveDir/output/done/velodyne/"
  # the below files would normally be populated during the evaluation of the SUTs, but that is not available at this time
  docker-compose exec gen_lidar_tests bash -c "rm -rf $newSaveDir/output/current"
  docker-compose exec gen_lidar_tests bash -c "rm -rf $newSaveDir/output/staging"
  docker-compose exec gen_lidar_tests bash -c "rm -rf $newSaveDir/output/results"
  docker-compose exec gen_lidar_tests bash -c "rm -rf $newSaveDir/output/done/pred"
  docker-compose exec gen_lidar_tests bash -c "rm -rf $newSaveDir/output/done/mutatedPred"
  # the Xvfb parts are to account for the fact we are running in a container without proper display access
  docker-compose exec gen_lidar_tests bash -c "(pgrep -x Xvfb >/dev/null || Xvfb :0 -screen 0 1024x768x24 -ac +extension GLX +render -noreset &) && python3 /root/genLidarTestTool/controllers/finalVisualize/finalVisualization.py -binPath /root/selected_data/semantic_kitti_pcs/dataset/sequences -labelPath /root/selected_data/semantic_kitti_labels/dataset/sequences -mdb /root/mongoconnect.txt -saveAt $outputDir -toolOutputPath $outputDir -vis_all"
done