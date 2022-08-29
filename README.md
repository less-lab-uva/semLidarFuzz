# Semantic LiDAR Fuzzer

Tool for the Semantic LiDAR Fuzzing paper

---

## Setup


### 0. System Requirements
- Ubuntu (experiments performed on Ubuntu 18.04)
- Nvidia GPU (experiments performed with GeForce GTX 1080 Ti GPU)
- osmesa (For visualizer) installed https://pyrender.readthedocs.io/en/latest/install/index.html


### 1. Set up Python Virtual Environment
- install python3
  - sudo apt-get install python3-distutils python3-pip python3-dev python3-venv
  - Note tested with Python 3.6.9
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
    - Download from: https://drive.google.com/file/d/10eEmiyYQqCO2_YM2jnL56ATsueH7w14k/view?usp=sharing
    - Matching mongodb assets collection (import) https://drive.google.com/file/d/1rrvx38dxImwe3H0epGvw73P97eec1xE3/view?usp=sharing
- NOTE the instances must match mongodb instances preloaded


#### 3.3 Model Original Predictions
- Manual prestep
    - Navigate to controllers/modelBasePred to create the prediction files for the model
- Premade
    - Download from: https://drive.google.com/file/d/1pqXz62NXroPvrM43TXwMXz0LLLXXMt50/view?usp=sharing



### 4. Set up SUTs
- Create a directory to serve as the base of all your models
- Clone all model Dockers you'd like to utilize into the same directory 
- Follow the setup instructions found in their readme's

| Model | Abbreviation | Rank with code | Rank | Fork |
| ----- | ------------ | -------------- | ----------------- | ---- |
| Cylinder3D | cyl | 1 | 3 | https://github.com/GarrettChristian/Cylinder3D |
| SPVNAS | spv | 2 | 4 | https://github.com/GarrettChristian/spvnas |
| SalsaNext | sal | 5 | 11 | https://github.com/GarrettChristian/SalsaNext |
| SqueezeSegV3 | sq3 | 7 | 15 | https://github.com/GarrettChristian/SqueezeSegV3 |
| PolarSeg | pol | 8 | 20 | https://github.com/GarrettChristian/PolarSeg |
| RandLA-Net | ran | 9 | 21 | https://github.com/GarrettChristian/RandLA-Net |




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

## Tool Diagrams

### Pre Processing, Asset Selection
![Asset Selection](https://github.com/GarrettChristian/lidarTest2/blob/main/diagrams/AssetSelection.jpg)

### Pre Processing, Original Model Predictions
![Orginal Model Predictions](https://github.com/GarrettChristian/lidarTest2/blob/main/diagrams/OriginalPredictions.jpg)

### Test Case Generation
![Test Case Generation](https://github.com/GarrettChristian/lidarTest2/blob/main/diagrams/TestCaseGeneration.jpg)

### Evaluation
![Evaluation](https://github.com/GarrettChristian/lidarTest2/blob/main/diagrams/Evaluation.jpg)

### Overview
![Overview](https://github.com/GarrettChristian/lidarTest2/blob/main/diagrams/Pipeline.jpg)

### Component Flow Overview SemFuzz
![Eval File System](https://github.com/GarrettChristian/lidarTest2/blob/main/diagrams/ComponentFlowSemFuzz.jpg)

### Eval File System Dataflow
![Eval File System](https://github.com/GarrettChristian/lidarTest2/blob/main/diagrams/FileSystemEvalDataFlow.jpg)


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

### SalsaNext
- GitHub: https://github.com/slawomir-nowaczyk/SalsaNext

### SqueezeSegV3
- GitHub: https://github.com/chenfengxu714/SqueezeSegV3

### PolarSeg
- GitHub: https://github.com/GarrettChristian/PolarSeg

### RandNet-LA
- GitHub: https://github.com/QingyongHu/RandLA-Net

### UVA Less Lab
- https://less-lab-uva.github.io/



---


