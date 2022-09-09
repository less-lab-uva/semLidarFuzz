# Generating Realistic and Diverse Tests for LiDAR-Based Perception Systems (Tool)

Tool for Generating Realistic and Diverse Tests for LiDAR-Based Perception Systems.

## Tool Inputs
The tool takes as input a set of labeled LiDAR point clouds as described in Sections II-A and II-B. 
This implementation uses the [SemanticKITTI](http://www.semantic-kitti.org/) data set.
Each of the inputs consists of a matched `.bin` file containing the point cloud with its intensities and `.label` file containing the semantic labeling of that point cloud.
These are the PC and ExpSem described in the paper.

### Resource collection
The tool begins by running Resource Collection (Section II-B) on the existing data set to identify additional entities that exist in the data set and to filter the list of entities to those suitable for use in mutation.
This will populate the data base with the filtered entities, and will re-write the `.label` files in place with the additional entities identified.

This process only needs to run once for a given data set. Further details are available in `./genLidarTestTool/controllers/extractInstances`.
Resource Collection is automatically performed using the `./tool_demo.sh` script for a subset of the SemanticKITTI data set, but would need to be performed manually for using the full data set.

## Tool Outputs
### Mutation Generation
The tool as implemented currently explores 7 combinations of the basic mutation operations, as outlined in Section VI and Table III.
Within the output directory, each run of a mutation will produce a folder named `<mutation name>_<timestamp>/output/`. 
This folder contains several directories used for intermediate result calculation including `current`, `results`, and `staging`. 
The final outputs will be in the `done/` and `finalvis/` folders. These are organized as:

```
- <mutation name>_<timestamp>/
  - output/
    - done/  # contains matched pairs of 
      - labels/
        - <mutation uuid>-<mutation name>.bin  # PC'
      - velodyne/
        - <mutation uuid>-<mutation name>.bin  # ExpSem'
    - finalvis/<mutation_name>/
      - <mutation uuid>-<mutation_name>.png  # collation of 2D range image projection of the mutation showing PC, PC', ExpSem, and ExpSem'
```

### Performance Evaluation
The tool also contains code to automatically evaluate the performance of a suite of SUTs on the test cases generated.
Each SUT is run on the initial PC, ExpSem pairs as a preprocessing step. 
Then, as outlined in Section II-D-1, the mutation is performed on both the point cloud and the tool's initial labeling to obtain PC', MUT(SUT(PC)). 
Then, the SUT is evaluated on the new point cloud and the score is evaluated as described in Equation 3.

For each mutation, a `<mutation name>_accuracy.csv` and `<mutation name>_jaccard.csv` are generated summarizing the performance of the SUTs under that metric.
The CSV captures the performance at different levels (called "buckets" in the CSV) corresponding to the epsilon values described in Section IV-C: (1,2], (2,3], (3,4], (4,5], (5,100]
For the automatic false positive detection discussed in RQ2, each CSV records the mutations where the SUTs failed together. 

## Running the Demo (containerized)

The [/.tool directory](./tool) contains the source code for the tool as well as a script (`./tool_demo.sh`) for running a minimal complete example of the mutations implemented in the tool and explored in the study.
The tool begins by performing Resource Collection (Approach in Section II-B, Implementation in Section III-A), then generates the 7 mutations discussed in Section VI and Table III.
The tool demo script does not run the SUTs; instructions on how to run the SUT Performance Evaluation portions (Section II-D) are available, though cannot be automated due to anonymization efforts as the tools' source was modified to produce a consistent output format for the tool.
Additional instructions will be made available upon acceptance.

The demo scripts use [Docker and Docker Compose](https://docs.docker.com/compose/install/) and these must be installed.
The docker script will download a small subset of the SemantiKITTI dataset, run Resource Collection on this subset, and then generate 5 mutations of each type.
The selected data will be downloaded in `./selected_data/` and tool demo output will be produced in `./sample_tool_output/`. 
The output contains the raw `bin` and `label` files, along with visualizations in the `final_viz` folders.

Within the `./selected_data/` folder, the `bin` files are the raw LiDAR point clouds with intensities, and the `label` files contain the ground truth semantic labeling with instances included in the SemanticKITTI format.
After running the Resource Collection phase, the `label` files will be modified in place to contain the additional entities identified (Section II-B).

Within the `./sample_tool_output/` folder, the new mutations will each be in separate folders of the form `<mutation name>_<timestamp>/`. 
Each mutation folder will contain a `/output/done/` folder that contains a set of  


To run the tool demo, use the following command. Building the Docker containers will take ~10 minutes, downloading and running Resource Collection will take ~10 more minutes, and then running the mutations will take ~10 more. There will be progress announcements throughout.
```bash
./tool_demo.sh
```


---
# Running Locally and Evaluating SUTs
The below sections contain information on how to run the tool including SUT evaluation. However, the SUTs are not available upon submission due to anonymization as they were edited to produce consistent output format.
The SUT code integration will be made available upon release.

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
python3.6 -m venv lidar_venv
source lidar_venv/bin/activate
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
- From the `genLidarTestTool` directory run `. setup.sh` (sets up the PYTHONPATH for the tool)
- in the run file alter the arguments to match your setup
- ./runToolAndSUTs.sh
    - python genLidarTests.py [args] generates mutations and evaluates them
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


