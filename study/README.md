# Study Information
This folder contains information about the study set up and results, as well as Python code for generating the figures from the paper.

## Downloading Study Data and Generating Figures
This directory contains a Docker compose setup that will download the study data from Google Drive and generate the figures from the paper (and others).
This requires that [Docker and Docker Compose](https://docs.docker.com/compose/install/) are installed on your system. Once installed, the below script
to download the study data to `./study_data./`, generate the figures found in `figures`, and print the LaTeX definitions of the tables to the console.

Configuring Docker and downloading the data used to generate the figures will take ~10 minutes. 
The figure generation should take ~1 minute.
There will be progress updates throughout.

```bash
./generate_figures.sh
```

The console output for running this command which contains the tables shown in the paper are in [output.txt](output.txt).
The figures generated are shown in [figures/](./figures).

### The study_data folder
The `./study_data/` folder contains the mutations generated and SUTs' performances evaluated for the study described in Section IV.
For information about the format of this folder and what information it contains, please see the `../tool/` [README](../tool/README.md).

### Index of Figures
|Figure Name| Description | In paper |
|-----------|-------------|----------|
|1 SUT_overlap.png| Pie chart of failures at highest severity (>5%) broken down by SUTs when only 1 SUT failed ||
|2 SUTs_overlap.png| Pie chart of failures at highest severity (>5%) broken down by which pair of SUTs failed ||
|3 SUTs_overlap.png| Pie chart of failures at highest severity (>5%) broken down by which set of 3 SUTs failed ||
|4 SUTs_overlap.png| Pie chart of failures at highest severity (>5%) broken down by which set of 4 SUTs failed ||
|5 SUTs_overlap.png| Pie chart of failures at highest severity (>5%) broken down by which set of 5 SUTs failed (this is all SUTs)||
|overlap_by_sut.png| Pie charts breaking down what groupings of SUTs failed together ||
|overlap_counts.png| Pie charts breaking down automatic false positive analysis for all mutations |Table IV|
|Total Overlap.png| Pie chart breaking down what groupings of SUTs failed together aggegated across mutations ||
|Add Mirror Rotate_horiz.png| Histogram of failures for the Add Mirror Rotate mutation by failure threshold||
|Add Mirror Rotate.png|Histogram of failures for the Add Mirror Rotate mutation by failure threshold||
|Add Mirror Rotate Overlap.png| Pie charts showing the automatic false positive analysis for Add Mirror Rotate||
|Add Rotate_horiz.png| Histogram of failures for the Add Rotate mutation by failure threshold ||
|Add Rotate.png| Histogram of failures for the Add Rotate mutation by failure threshold ||
|Add Rotate Overlap.png| Pie charts showing the automatic false positive analysis for Add Rotate||
|biggest_failures_horiz.png| The failures at highest severity (>5%) per mutation | Fig. 6 |
|biggest_failures.png|The failures at highest severity (>5%) per mutation||
|failure_counts_horiz.png| Figure showing all failure counts by threshold for all mutations ||
|failure_counts.png| Figure showing all failure counts by threshold for all mutations ||
|Remove_horiz.png|Histogram of failures for the Add Mirror Rotate mutation by failure threshold||
|Remove.png|Histogram of failures for the Add Mirror Rotate mutation by failure threshold||
|Remove Overlap.png|Pie charts showing the automatic false positive analysis for Remove||
|Sign Replace_horiz.png|Histogram of failures for the Sign Replace mutation by failure threshold||
|Sign Replace.png|Histogram of failures for the Sign Replace mutation by failure threshold||
|Sign Replace Overlap.png|Pie charts showing the automatic false positive analysis for Sign Replace||
|time_per_mutation.png| Bar chart showing time to perform each mutation | Section IV-C-3 (RQ3) |
|Total_horiz.png| Failure counts at different thresholds | Fig. 5 |
|Total.png|Failure counts at different thresholds||
|Vehicle Deform_horiz.png|Histogram of failures for the Vehicle Deform mutation by failure threshold||
|Vehicle Deform.png|Histogram of failures for the Vehicle Deform mutation by failure threshold||
|Vehicle Deform Overlap.png|Pie charts showing the automatic false positive analysis for Vehicle Deform||
|Vehicle Intensity_horiz.png|Histogram of failures for the Vehicle Intensity mutation by failure threshold||
|Vehicle Intensity.png|Histogram of failures for the Vehicle Intensity mutation by failure threshold||
|Vehicle Intensity Overlap.png|Pie charts showing the automatic false positive analysis for Vehicle Intensity||
|Vehicle Scale_horiz.png|Histogram of failures for the Vehicle Scale mutation by failure threshold||
|Vehicle Scale.png|Histogram of failures for the Vehicle Scale mutation by failure threshold||
|Vehicle Scale Overlap.png|Pie charts showing the automatic false positive analysis for Vehicle Scale||



## Study Set Up

### Resources Collected from SemanticKITTI
This table discusses the number of initial resources compared to the number ultimately selected for mutation.
Resource Collection is discussed in Section II-B, and the table below is discussed in Section IV-B.

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

|Parameter | Value | Discussion |
|--------|----------|------------|
|*minPointThreshold* | 20 points  |  Smaller entities may not contain enough context for mutation. | 
|*distThresh* | 40m  | Beyond this distance the points may be affected by noise. |
|*occlBuffer* | 25%  | By using a small over-approximation, we improve the invariants strictness.  |
|*minSignPoints* | 10 points | Due to the smaller nature of signs compared to other entities, the initial point threshold is reduced to allow for richer identification |
|*signSizeThreshold* | 3m  | Identified based on the size of real-life signs |
|*addOcclusionThreshold* | 10 points  | The small allowance balances the stringency of the invariant with the ability to generate mutations, smaller amounts are more stringent |
|*groundThreshold* | 33%  | Since objects may extend into other regions, requiring 33% to be in the specified area allows for variation while respecting invariants.|
|*groundDistanceThreshold* | 5m  | Determined by LiDAR intrinsics, with small buffer added |
|*removePointsAboveThresh* | 30 points  | Identified as a reasonable balance between stringency and ability to generate, smaller amounts are more stringent. |
|*invalidReplacementClasses* | car, bicycle, bus, motorcycle, truck, other-vehicle, moving-car, moving-bus, moving-truck, moving-other-vehicle, building, fence, other-structure, trunk, pole, traffic-sign, other-object  | Since these classes are often part of cohesive entities, they may not be disconnected and used for filling.|
|*intensityMutateThresh* | 0.8  | Determined based on examining un-paintable areas in existing data, e.g. license plates. |
|*intensitySubThresh* | 0.1  | Not an invariant - selected to produce variety in intensity mutations |
|*minIntensityThresh* | 0.1  | Not an invariant - the min amount to alter is chosen to produce sufficient variety from prior tests. |
|*maxIntensityThresh* | 0.3  | The max amount to alter invariant is chosen so that the new entity is within realistic limits. |
|*minDeformThresh* | 5%  | Not an invariant - the min number of points to alter is chosen to produce sufficient variety from prior tests. |
|*maxDeformThresh* | 12%  | The max amount to deform is limited as natural deformations are limited in size. | 
|*deformNoiseMean* | 0.05m  | Chosen based on the average size of vehicles. |
|*deformNoiseStdDev* | 0.04m  | Chosen based on the average size of vehicles. |
|*scaleAmount* | 105%  | Chosen based on the observed trends in vehicle sizes over the past 20 years. |
|*maxScalePointsThreshold* | 10000 points  | Chosen due to computational limits, larger values were found to be computationally infeasible. |
|*minScalePointThreshold* | 20 points  | Smaller entities may not contain enough definition for enlargement |
|*minSignHeight* | -1m  | Relative to the LiDAR mount height; lower signs may not be in the correct semantic context. |
|*signSizeAllowance* | 2m  | Buffer to allow for alterations while maintaining size constraints. Smaller is more stringent. |
|*minSignPointThreshold* | 15 points | Smaller signs may not contain enough definition for alteration. |

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