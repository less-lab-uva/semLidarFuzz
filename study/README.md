# Study Information
This folder contains information about the study set up and results, as well as Python code for generating the figures from the paper.

## Study Set Up

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