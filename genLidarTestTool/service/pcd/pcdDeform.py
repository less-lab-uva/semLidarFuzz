"""
pcdDeform
Deform Mutation

@Date 6/23/22
"""


import math
import numpy as np
import open3d as o3d
import random

import domain.config as config

# --------------------------------------------------------------------------
# Deform


"""
deform

Pushes points around a base point away from the sensor
Resembles a dent
http://www.open3d.org/docs/release/tutorial/geometry/kdtree.html
"""
def deform(asset, details, deformPoint, percentDeform, deformMu, deformSigma, deformSeed):

    pcdAsset = o3d.geometry.PointCloud()
    pcdAsset.points = o3d.utility.Vector3dVector(asset)

    
    # Select point to deform from
    pointIndex = deformPoint
    if (not deformPoint):
        pointIndex = np.random.choice(asset.shape[0], 1, replace=False)
    # print(pointIndex)

    # Get the amount of points to deform
    assetNumPoints = np.shape(asset)[0]
    if (not percentDeform): # 0.05 - 0.12
        percentDeform = random.uniform(config.DEFORM_MIN_CHANGE, config.DEFORM_MAX_CHANGE)
    k = int(assetNumPoints * percentDeform)
    
    # Get the K nearest points
    pcd_tree = o3d.geometry.KDTreeFlann(pcdAsset)
    [k, idx, _] = pcd_tree.search_knn_vector_3d(pcdAsset.points[pointIndex], k)
    # np.asarray(pcdAsset.colors)[idx[1:], :] = [0, 0, 1]

    # Setting seed on random generator for reproducbility
    # https://towardsdatascience.com/stop-using-numpy-random-seed-581a9972805f
    if (not deformSeed):
        deformSeed = np.random.randint(1000000000000)
    npRng = np.random.default_rng(deformSeed)

    # mu Sigma
    mu = deformMu
    if (not deformMu):
        mu = config.DEFORM_MU # 0.05
    sigma = deformSigma
    if (not deformMu):
        sigma = config.DEFORM_SIGMA # 0.04

    # noise = np.random.normal(mu, sigma, (k))
    noise = npRng.normal(mu, sigma, (k))
    noise = np.sort(noise)[::-1]
    details["deformPercent"] = percentDeform
    details["deformPoint"] = int(pointIndex[0])
    details["deformPoints"] = k
    details["deformMu"] = mu
    details["deformSigma"] = sigma
    details["deformSeed"] = deformSeed
    details["pointsAffected"] = k

    for index in range(0, len(idx)):
        asset[idx[index]] = translatePointFromCenter(asset[idx[index]], noise[index])


    return asset, details




"""
translatePointFromCenter
Translate a point to a new location based on the center

# https://math.stackexchange.com/questions/175896/finding-a-point-along-a-line-a-certain-distance-away-from-another-point
"""
def translatePointFromCenter(point, amount):

    # pcdPoints = o3d.geometry.PointCloud()
    # pcdPoints.points = o3d.utility.Vector3dVector(pointsCopy)
    # obb = pcdPoints.get_oriented_bounding_box()
    # centerOfPoints = obb.get_center()
    
    # Note the 0 here is the center point
    vX = point[0] - 0
    vY = point[1] - 0

    uX = vX / math.sqrt((vX * vX) + (vY * vY))
    uY = vY / math.sqrt((vX * vX) + (vY * vY))

    newPoint = np.array([0, 0, point[2]])
    newPoint[0] = point[0] + (amount * uX)
    newPoint[1] = point[1] + (amount * uY)

    return newPoint
