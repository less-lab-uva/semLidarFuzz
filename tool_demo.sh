printf "Setting up Docker container\n"
docker-compose up --build -d
if test -f ".keep" ; then
  printf "One time setup has already been completed, generating test cases\n"
else
  printf "Downloading selected data to use for generating tests\n"
  docker-compose exec gen_lidar_tests bash -c "mkdir /root/selected_data 2>/dev/null"
  docker-compose exec gen_lidar_tests bash -c "python3 -c 'import gdown; gdown.download(id=\"1eRayHOx2sG4EaLzZ2daU8caKhqCoKkBD\", output=\"/root/selected_data.tar.xz\", quiet=False)' && printf \"Extracting selected data to ./selected_data, this may take a moment\n\" && tar -xf /root/selected_data.tar.xz -C /root/selected_data --strip-components=1 --checkpoint=.250 && rm /root/selected_data.tar.xz" && \
  printf "\nPerforming Resource Collection\n" && \
  docker-compose exec gen_lidar_tests bash -c "python3 /root/genLidarTestTool/controllers/extractInstances/instanceExtractorV4.py -mdb /root/mongoconnect.txt -labelPath /root/selected_data/semantic_kitti_labels/dataset/sequences -binPath /root/selected_data/semantic_kitti_pcs/dataset/sequences" && \
  printf "Resource Collection" && \
  touch .keep
fi
# Total count of total mutations to generate
count=5
saveDir=/root/sample_tool_output
printf "Generating $count mutations for each type and saving to ./sample_tool_output\n"
for mutation in "VEHICLE_INTENSITY" #"ADD_ROTATE" "ADD_MIRROR_ROTATE" "SCENE_REMOVE" "SIGN_REPLACE" "VEHICLE_DEFORM" "VEHICLE_SCALE"
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