# Generating Realistic and Diverse Tests for LiDAR-Based Perception Systems

Tool for Generating Realistic and Diverse Tests for LiDAR-Based Perception Systems

---

## Setup


### 0. System Requirements
- Ubuntu (experiments performed on Ubuntu 18.04)
- Nvidia GPU (experiments performed with NVIDIA TITAN RTX GPU)


### 1. Set up Python Virtual Environment
- install python3
  - sudo apt-get install python3-distutils python3-pip python3-dev python3-venv
  - Experiments run with with Python 3.6.9
```bash
sudo apt install python3.6-venv
python3.6 -m venv semFuzzLidar_venv
source semFuzzLidar_venv/bin/activate
pip3 install --upgrade pip
pip3 install -r requirements.txt
```

### 2. Connect & Prepare Mongodb
- Get a mongodb instance (Free 500 mb instance provided at mongodb atlas)
- Create database named: "lidar_data"
- Within that database create collections named:
    - asset_metadata4
    - assets4
    - final_data
    - mutations
- Create a mongodb connection file called "mongoconnect.txt" that contains one line, the url connection string
    - Sample: mongodb://username:password@host:port/?authSource=admin
    - Format: mongodb://[username:password@]host1[:port1][,...hostN[:portN]][/[defaultauthdb][?options]]
    - https://www.mongodb.com/docs/manual/reference/connection-string/
- Note downloading mongodb compass is helpful for visualization of data and importing collections:  https://www.mongodb.com/products/compass


### 3. Get / Generate Required Data
#### 3.1 LiDAR Bin Scans
- Can be downloaded from the SemanticKITTI website: http://www.semantic-kitti.org/dataset.html#download


#### 3.2 Ground Truth Semantic Labels with Instances
- Manual prestep
    - Download from the SemanticKITTI website: http://www.semantic-kitti.org/dataset.html#download
    - Navigate to controllers/extractInstances to create the label files to match
- Premade
    - Download from: 
    - Matching mongodb assets collection (import) 
- NOTE the instances must match mongodb instances preloaded


#### 3.3 Model Original Predictions
- Manual prestep
    - Navigate to controllers/modelBasePred to create the prediction files for the model
- Premade
    - Download from: 



### 4. Set up SUTs
Directions for setting up from source will be provided with full release.
However, for anonymization, until then please use the following Docker containers:


---



## Running the tool

- Activate python venv
- From tool directory run ". setup.sh" (sets up the PYTHONPATH for the tool)
- in the run file alter the arguments to match your setup
- ./fullSemLiDARFuzz
    - python semFuzzLidar.py [args] generates mutations and evaluates them
    - python finalVisualization.py [args] visualizes the top results reported by the finalDetails object produced (see controllers/finalVisualize)
    - python produceCsv.py [args] creates csv files created from the finalDetails object produced (see controllers/analytics)
    - Note see the controller readmes for more explantation on each of the above scripts 


---

---
## Project Structure

- controllers - Contains the main script for the mutation tool and controllers for various tool functionality (visit these controller folder's readme for a more detailed overview)
    - analytics - creates csv distilations of runs 
    - extractInstances - preprocessing step scripts to seed db and create alterative label files
    - finalVisualize - creates images to visualize the results
    - modelBasePred - scripts to get the predictions from the models
    - mutationTool - main mutation tool controller
- data - Contains the classes that interact with the LiDAR data and repositories for mongodb
- domain - Knowlege required for the tool, enums, constants, config, and the toolSessionManager
- service - Operations performed by the tool
    - eval - evaluation actions
    - models - runners for all model dockers
    - pcd - operations on point clouds, mutations


---
## Adding a New Model
- Requirements
    - Should be from the SemanticKITTI website leaderboard http://www.semantic-kitti.org/tasks.html#semseg
    - Should have publicly released code
    - Should have a pretrained model
- Test script should be modified to point at sequence 00 in a test mode
- The model should save predictions to a provided directory with the same file name as the scan bin file
- Docker
    - All model docker images are their directory name lower case + "_image"
    - Container is directory name lower case
    - Build with docker build . -t \<container name\>
- Code changes
    - Add model to models enum
    - Add constant for model directory name
    - Create a new model runner with the run command



---
## Data guide - SemanticKITTI
- See https://github.com/PRBonn/semantic-kitti-api for a more detailed breakdown
- Label Map Class guide: https://docs.google.com/spreadsheets/d/1EQWp-C2e15yuzHAFa-iXMrImnfBEGQ60NGzMaLEwSPQ/edit?usp=sharing
- Labels [.label] list of uint32 values for each point, lower 16 bits semantics, upper 16 bits are the instance
- Scans [.bin] list of float32 points in [x,y,z,remission] format


---
## Relevant Links

### SemanticKITTI
- SemanticKITTI website: http://www.semantic-kitti.org/index.html
- SemanticKITTI API: https://github.com/PRBonn/semantic-kitti-api
- SemanticKITTI Paper: https://arxiv.org/abs/1904.01416

### Cylinder3D
- GitHub: https://github.com/xinge008/Cylinder3D
- Required SpConv https://github.com/traveller59/spconv/tree/v1.2.1

### SPVNAS
- GitHub: https://github.com/mit-han-lab/spvnas
- Required Torch Sparse (version 1.4.0 used) Github: https://github.com/mit-han-lab/torchsparse

### JS3C-Net
- GitHub: https://github.com/yanx27/JS3C-Net

### SalsaNext
- GitHub: https://github.com/slawomir-nowaczyk/SalsaNext

### SqueezeSegV3
- GitHub: https://github.com/chenfengxu714/SqueezeSegV3


---


