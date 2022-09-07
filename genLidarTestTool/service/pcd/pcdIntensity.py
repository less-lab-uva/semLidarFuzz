"""
pcdIntensity
Intensity Mutation

@Date 6/23/22
"""


import numpy as np
import random

from sklearn.neighbors import NearestNeighbors

import domain.config as config


# --------------------------------------------------------------------------
# Intensity


"""
intensityChange

Changes the intensity of a section of the vehicle
"""
def intensityChange(intensityAsset, details, intensityMod):

    # Create a mask that represents the portion to change the intensity for
    mask = np.ones(np.shape(intensityAsset), dtype=bool)

    # if (type in semanticMapping.instancesVehicle.keys()):    
    dists = nearestNeighbors(intensityAsset, 2)
    class0 = intensityAsset[dists[:, 1] == 0]
    class1 = intensityAsset[dists[:, 1] == 1]

    # Take majority class
    mask = dists[:, 1] == 0
    if np.shape(class0)[0] < np.shape(class1)[0]:
        mask = dists[:, 1] == 1

    # Threshold for license intensity if NN didn't catch it ( >= 0.8)
    mask = np.where(intensityAsset >= config.INTENSITY_IGNORE_THRESHOLD, False, mask)

    average = np.average(intensityAsset[mask])
    
    mod = random.uniform(config.INTENSITY_MIN_CHANGE, config.INTENSITY_MAX_CHANGE)
    if average > .1:
        mod = mod * -1

    # For given recreation
    if (intensityMod != None):
        mod = intensityMod

    details["intensity"] = mod
    details["pointsAffected"] = int(np.shape(intensityAsset[mask])[0])
    

    intensityAsset = np.where(mask, intensityAsset + mod, intensityAsset)
    intensityAsset = np.where(intensityAsset < 0, 0, intensityAsset)
    intensityAsset = np.where(intensityAsset > 1, 1, intensityAsset)


    return intensityAsset, details


"""
nearestNeighbors
Seperates the values into k groups using nearest neighbors

https://stackoverflow.com/questions/45742199/find-nearest-neighbors-of-a-numpy-array-in-list-of-numpy-arrays-using-euclidian
"""
def nearestNeighbors(values, nbr_neighbors):

    zeroCol = np.zeros((np.shape(values)[0],), dtype=bool)
    valuesResized = np.c_[values, zeroCol]

    nn = NearestNeighbors(n_neighbors=nbr_neighbors, metric='cosine', algorithm='brute').fit(valuesResized)
    dists, _ = nn.kneighbors(valuesResized)

    return dists




