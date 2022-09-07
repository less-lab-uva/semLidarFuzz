# Study Information
This folder contains information about the study set up and results, as well as Python code for generating the figures from the paper.

## Downloading Study Data and Generating Figures
This directory contains a Docker compose setup that will download the study data from Google Drive and generate the figures from the paper (and others).
This requires that [Docker and Docker Compose](https://docs.docker.com/compose/install/) are installed on your system. Once installed, the below script
to download the study data to `study_data`, generate the figures found in `figures`, and print the LaTeX definitions of the tables to the console.

```bash
./generate_figures.sh
```

## Study Set Up

### Resources Collected from SemanticKITTI
|Type Name|Total Count|Selected Count|%|
|---|---|---|---|
|car|205784|44893|21.8% |
|traffic-sign|0|8443|-|
|moving-car|8933|3503|39.2% |
|moving-person|5895|1534|26.0% |
|moving-bicyclist|2874|1368|47.6% |
|other-vehicle|10478|888|8.5% |
|motorcycle|4586|749|16.3% |
|person|6339|486|7.7% |
|moving-motorcyclist|555|473|85.2% |
|truck|2643|421|15.9% |
|bicycle|10602|449|4.2% |
|moving-bus|79|45|57.0% |
|moving-other-vehicle|220|36|16.4% |
|motorcyclist|171|20|11.7% |
|moving-truck|172|15|8.7% |
|bicyclist|6|0|0.0% |
|bus|10|0|0.0% |
|**Total**|**259347**|**63323**|**24.4%**|

### Study Parameters
During the study, the variables discussed in the Implementation Section were given the corresponding values below.
These values were chosen through small-batch experimentation to determine reasonable default values for a larger-scale study.
Individual testing goals, or testing using different data sets may necessitate changes to these values.  

|Parameter | Value |
|--------|----------|
|*minPointThreshold* | 20 points  |
|*distThresh* | 40m  |
|*occlBuffer* | 25%  |
|*minSignPoints* | 10 points |
|*signSizeThreshold* | 3m  |
|*addOcclusionThreshold* | 10 points  |
|*groundThreshold* | 33%  |
|*groundDistanceThreshold* | 5m  |
|*removePointsAboveThresh* | 30 points  |
|*invalidReplacementClasses* | car, bicycle, bus, motorcycle, truck, other-vehicle, moving-car, moving-bus, moving-truck, moving-other-vehicle, building, fence, other-structure, trunk, pole, traffic-sign, other-object  |
|*intensityMutateThresh* | 0.8  |
|*intensitySubThresh* | 0.1  |
|*minIntensityThresh* | 0.1  |
|*maxIntensityThresh* | 0.3  |
|*minDeformThresh* | 5%  |
|*maxDeformThresh* | 12%  |
|*deformNoiseMean* | 0.05m  |
|*deformNoiseStdDev* | 0.04m  |
|*scaleAmount* | 105%  |
|*maxScalePointsThreshold* | 10000 points  |
|*minScalePointThreshold* | 20 points  |
|*minSignHeight* | -1m  |
|*signSizeAllowance* | 2m  |
|*minSignPointThreshold* | 15 points |

## Generating Figures 
This package is used to generate the figures used in the paper.
Due to compatibility issues, the rest of the system uses Python 3.6.9.
However, in order to leverage the new features in later versions of Matplotlib, the figure generation uses Python 3.10.
A new venv must be created for the figure generation.

```bash
sudo apt install python3.10-venv
python3.10 -m venv figure_venv
source figure_venv/bin/activate
pip3 install --upgrade pip
pip3 install -r requirements.txt
```