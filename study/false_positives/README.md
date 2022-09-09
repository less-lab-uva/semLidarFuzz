# Discussion of False Positives
As discussed in the paper, humans are not well suited to judge the realism of LiDAR point clouds.
Here we give several examples of true and false positives identified in the study.


## Typo in Table IV in the paper
***NOTE***: There is a typo in Table IV of the table, where the data are off by 1 percentage point for the Jaccard metric. The correct table is contained in the output.txt and replicated here:

|Mutation|Acc. TP | Acc. FP | Jacc. TP | Jacc. FP |
|--------|--------|---------|----------|----------|
|Add Rotate| 39 |  2| 634 |  77 |
|Add Mirror Rotate| 42 |  2| 672 |  79 |
|Remove| 6 |  ---| 26 |  --- |
|Vehicle Intensity| 63 |  2| 178 |  4 |
|Vehicle Deform| 5 |  ---| 10 |  --- |
|Vehicle Scale| 12 |  ---| 81 |  14 |
|Sign Replace| --- |  ---| 37 |  1 |
|Total| 167 |  6| 1638 |  175 |
| % | (97%) |  (3%)| (90%) |  (10%) |


## False Positives
As discussed in Section IV-C-3, the voting mechanism sets a threshold, V, for determining if a test case is a false positive based on if V or more SUTs failed on that test case.
In Table IV, shown above, we use V=3 as the threshold. Below we examine several examples of false positives found:

### Accuracy Metric
Under the accuracy metric we find only 6 of the 167 failures are false positives. We examine two examples below:

#### Example 1
In the below example, the mutation takes a point cloud containing a truck and alters the intensity of the points so that they are at a much lower intensity than before.
Looking at the image, we can clearly identify that the truck is now appears much darker; however, it appears to be at a similar intensity level as the car in the background behind it.
This very clearly demonstrates how humans are ill-suited for judging realism for LiDAR, as we have no inherent intuition for intensities.

Original Labeling:
![Original Labeling](./images/actual-og-Xu84Tc9TwpGXeGaVt9ELY2-VEHICLE_INTENSITY.png)

Original Intensities:
![Original Intensities](./images/actual-og-intensity-Xu84Tc9TwpGXeGaVt9ELY2-VEHICLE_INTENSITY.png)

With Vehicle Intensities altered:
![With Intensities Altered](./images/actual-new-intensityXu84Tc9TwpGXeGaVt9ELY2-VEHICLE_INTENSITY.png)

The JS3C-Net (17.5%), SalsaNext (17.2%), and SqueezeNetV3 (14.9%) models failed on this test. 
For each of the SUTs, we see that they mislabeled different regions of the truck, confusing it for truck versus car versus bus.
Further, these mislabelings appear in splotches that do not seem to correlate with any specific aspect of the vehicle.

JS3C-Net Performance:
![JS3C-Net Performance](./images/js3c_gpu-new-Xu84Tc9TwpGXeGaVt9ELY2-VEHICLE_INTENSITY.png)

SalsaNext Performance:
![SalsaNext Performance](./images/sal-new-Xu84Tc9TwpGXeGaVt9ELY2-VEHICLE_INTENSITY.png)

SqueezeNetV3 Performance:
![SqueezeNetV3 Performance](./images/sq3-new-Xu84Tc9TwpGXeGaVt9ELY2-VEHICLE_INTENSITY.png)

#### Example 2
In the below example, the mutation takes a point cloud in which the vehicle is driving on a street and adds a car on the street partially in the grass.
Visually inspecting the new image, there is no clear indication why this might not be realistic.
The added vehicle appears partially off the roadway, but this is a reasonable location for the car; perhaps this vehicle had an accident and pulled off of the road into the grass.
The car appears large; however, this is the same distance that the car was in its original point cloud so that is realistic.
There are a few regions around the car where there are no LiDAR readings (shown in black), but this happens at various places around the image, so while this may be part of the issue it is not possible to intuit directly.

Original:
![Original Labeling](./images/actual-og-gWuMWhwsncBk4uagGpj2cK-ADD_ROTATE.png)

With Vehicle Added:
![Labeling with vehicle added](./images/actual-new-gWuMWhwsncBk4uagGpj2cK-ADD_ROTATE.png)

The Cylinder3D (15.1%), SPVNAS (7.0%), and SalsaNext (8.1%) models failed on this test. 
Their labelings are shown below. 
For each of the SUTs, we see that they mislabeled different regions of the added vehicle, confusing it for car versus bus versus building.


Cylinder3D Performance on new PC:
![Cylinder3D Performance](./images/cyl-new-gWuMWhwsncBk4uagGpj2cK-ADD_ROTATE.png)

SPVNAS Performance on new PC:
![SPVNAS Performance](./images/spv-new-gWuMWhwsncBk4uagGpj2cK-ADD_ROTATE.png)

SalsaNext Performance on new PC:
![SalsaNext](./images/sal-new-gWuMWhwsncBk4uagGpj2cK-ADD_ROTATE.png)

### Jaccard Metric
Under the accuracy metric we find only 175 of the 1638 failures are false positives. We examine two examples below:

#### Example 1
In the below example, the mutation adjusts the scale of the truck (purple) in the upper right of the image.
This is the only example where our intuition may tell us this could be a false positive.
We can see that in the updated image, the truck appears to have shrunk and left a hole shown in black.
Further investigation is required to understand what might have caused this issue.

Original:
![Original](./images/actual-og-o4hHBnZQuj4jLxo6Tz8aDh-VEHICLE_SCALE.png)

With Vehicle Scale Adjusted
![With Vehicle Scale Adjusted](./images/actual-new-o4hHBnZQuj4jLxo6Tz8aDh-VEHICLE_SCALE.png)

The Cylinder3D (5.7), SPVNAS (7.6), and JS3C-Net (7.5) models failed this test under the Jaccard metric.
In each case we can see that the SUT mislabeled the truck as either a bus (blue) or building (orange), which led to a large change in the Jaccard metric since there are no other trucks in the scene.

Cylinder3D Performance:
![Cylinder3D Performance](./images/cyl-new-o4hHBnZQuj4jLxo6Tz8aDh-VEHICLE_SCALE.png)

SPVNAS Performance:
![SPVNAS Performance](./images/spv-new-o4hHBnZQuj4jLxo6Tz8aDh-VEHICLE_SCALE.png)

JS3C-Net Performance:
![JS3C-Net Performance](./images/js3c_gpu-new-o4hHBnZQuj4jLxo6Tz8aDh-VEHICLE_SCALE.png)

#### Example 2
In the below example, the mutation adds a mirrored sign in the sidewalk on the right side of the image.
Although sidewalks are typically free from signs, this is still physically feasible in rare circumstances, and so it is difficult for a human to judge if there is something unrealistic about the way this sign appears in this context.
This may demonstrate how this method of determining false positives can over-estimate the amount of false positives as a very difficult but realistic test case may lead to multiple failures and thus be marked as a false positive.
In this case, perhaps the sign is entirely realistic but the uncommon placement of the sign has yielded multiple failures.

Original:
![Original](./images/actual-og-HJe3F3zsurqnDWGLY5wgMY-ADD_MIRROR_ROTATE.png)

With Added Mirrored Sign:
![With Added Sign](./images/actual-new-HJe3F3zsurqnDWGLY5wgMY-ADD_MIRROR_ROTATE.png)

The Cylinder3D (10.2), SalsaNext (10.0), and SqueezeNetV3 (9.6) failed this test under the Jaccard metric.
In each of the three cases we can see that the model mislabeled the added sign as building; since there are no other signs in the image, missing this class leads to a large change in the Jaccard metric.

Cylinder3D Performance:
![Cylinder3D Performance](./images/cyl-new-HJe3F3zsurqnDWGLY5wgMY-ADD_MIRROR_ROTATE.png)

SalsaNext Performance:
![SalsaNext Performance](./images/sal-new-HJe3F3zsurqnDWGLY5wgMY-ADD_MIRROR_ROTATE.png)

SqueezeNetV3:
![SqueezeNetV3 Performance](./images/sq3-new-HJe3F3zsurqnDWGLY5wgMY-ADD_MIRROR_ROTATE.png)