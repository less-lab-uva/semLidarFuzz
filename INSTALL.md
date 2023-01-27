# Running the Containerized Demo
For artifact evaluation or for a short demonstration of the tool, use the [./tool_demo.sh](./tool/tool_demo.sh) file.
This executable shell script will build, download, and setup all of the necessary dependencies using Docker Compose.
The [./tool README](./tool/README.md) contains more information.

While running, the script will output various messages detailing the status of the installation and tool run.
Building the Docker containers will take ~20 minutes, downloading and running Resource Collection will take ~10 more minutes, running the mutations will take ~10 more, and then the SUTs will take ~10 more.
Once initial builds have been completed, subsequent runs should take ~10 min. 
Note that warning/status messages may appear from internal components; these are normal.

Example Output (numbers quoted below may vary based on randomization/machine differences):
```
Setting up Docker container
Building gen_lidar_tests
...
Downloading selected data to use for generating tests
...
Performing Resource Collection
...
Ran for 00:07:41
Resource Collection Complete
Setting up SUTs
...
Starting Model Base Prediction Maker
...
Starting Model Evaluation Upload
...
DONE ACC JAC:

cyl
0.9391238636832958
0.5042026616496076
js3c_gpu
0.9387479595770283
0.4891203859190113
sal
0.9249892060509505
0.4406978101733467
sq3
0.9268331443619375
0.41221747658750213
...
Starting LiDAR Test Generation
...
Saving Results at: /root/sample_tool_output/VEHICLE_INTENSITY_2023_01_27-09_51_35
...
Starting LiDAR Test Generation
...
Saving Results at: /root/sample_tool_output/ADD_ROTATE_2023_01_27-09_52_55
...
Starting LiDAR Test Generation
...
Saving Results at: /root/sample_tool_output/ADD_MIRROR_ROTATE_2023_01_27-09_54_27
...
Starting LiDAR Test Generation
...
Saving Results at: /root/sample_tool_output/SCENE_REMOVE_2023_01_27-09_55_58
...
Starting LiDAR Test Generation
...
Saving Results at: /root/sample_tool_output/SIGN_REPLACE_2023_01_27-09_58_06
...
Starting LiDAR Test Generation
...
Saving Results at: /root/sample_tool_output/VEHICLE_DEFORM_2023_01_27-09_59_34
...
Starting LiDAR Test Generation
...
Saving Results at: /root/sample_tool_output/VEHICLE_SCALE_2023_01_27-10_00_53
...
Data has been saved to semLidarFuzz/tool/sample_tool_output.
Each mutation has a separate folder containing the SUT performance in csv files in the output/ folder.
The output/finalvis/<mutation_name>/ folder contains visualizations of the mutation as well as SUT performance.
Given the small number of mutations created during the demo, it is normal to not find any failures.
```
Below is an example of one of the generated visualizations:
<div style="white-space: nowrap">
  <img src="./images/GzpJLZyxEo5T3eWe33fvK6-ADD_MIRROR_ROTATE.png" width="300" alt="Example Visualization">
</div>

# Installing Locally
To install the tool locally, follow instructions in the [./tool README](./tool/README.md).
This requires additional manual support and is not recommended unless you are attempting to 