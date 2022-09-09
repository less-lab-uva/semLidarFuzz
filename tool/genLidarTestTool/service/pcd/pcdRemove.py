"""
pcdRemove
Remove Mutation

@Date 6/23/22
"""


import math
import numpy as np
import open3d as o3d

import service.pcd.pcdCommon as pcdCommon

import domain.semanticMapping as semanticMapping
import domain.config as config


# --------------------------------------------------------------------------
# Remove


"""
replaceBasedOnShadow

Removes an asset then replaces the area that was obscured 
Using the shadow split into two halves
"""
def replaceBasedOnShadow(asset, scene, intensity, semantics, instances, details, modelPredictions):

    # Get the objects shadow
    shadow = pcdCommon.getLidarShadowMesh(asset)
    shadowVertices = np.asarray(shadow.vertices)
    
    # Check above if this is a vehicle type
    # This avoids cases where is copies large chunks of road / sidewalk into the walls
    if (details["typeNum"] in semanticMapping.instancesVehicle.keys()): 
        shadowVerticesRaised = np.copy(shadowVertices)
        shadowVerticesRaised[:, 2] = shadowVerticesRaised[:, 2] + 1
        pcdShadowRaised = o3d.geometry.PointCloud()
        pcdShadowRaised.points = o3d.utility.Vector3dVector(shadowVerticesRaised)
        hullShadowRaised, _ = pcdShadowRaised.compute_convex_hull()
        # 70 veg, 50: 'building', 51: 'fence',
        maskAbove = (semantics == 70) | (semantics == 50) | (semantics == 51)
        sceneVegitation = scene[maskAbove]
        maskAbove = pcdCommon.checkInclusionBasedOnTriangleMesh(sceneVegitation, hullShadowRaised)

        if (np.sum(maskAbove) > config.REMOVE_POINTS_ABOVE_LIMIT):
            details["issue"] = "TOO MANY ABOVE {} ".format(np.sum(maskAbove))
            return False, None, None, None, None, details, None

    # Remove

    #  Get the asset's convex hull
    pcdAsset = o3d.geometry.PointCloud()
    pcdAsset.points = o3d.utility.Vector3dVector(asset)
    hull, _ = pcdAsset.compute_convex_hull()
    assetBox = pcdAsset.get_oriented_bounding_box()

    # Get the left and rightmost points from the perspective of the camera 
    leftPoint, rightPoint = pcdCommon.getLeftAndRightEdges(hull)

    # Provide two points in center of the current hull for when the two sides are split 
    midPoint = hull.get_center()
    midPointMaxZ = hull.get_center() 
    midPointMinZ = hull.get_center()
    midPointMaxZ[2] = assetBox.get_max_bound()[2]
    midPointMinZ[2] = assetBox.get_min_bound()[2] - 1

    # Sort the shadow points into left and right
    replaceLeftShadow = [midPointMaxZ, midPointMinZ]
    replaceRightShadow = [midPointMaxZ, midPointMinZ]
    for point in shadowVertices:
        if (pcdCommon.isLeft(midPoint, pcdCommon.centerCamPoint, point)):
            replaceLeftShadow.append(point)
        else:
            replaceRightShadow.append(point)

    # Validate that each side has enough points to be constructed into a mask (4 points min, otherewise open3d complains)
    if (len(replaceLeftShadow) < 4 or len(replaceRightShadow) < 4):
        details["issue"] = "Not enough points left {} or right {} shadow".format(len(replaceLeftShadow), len(replaceRightShadow))
        return False, None, None, None, None, details, None

    # Get the angles for left and right
    angleLeft = pcdCommon.getAngleRadians(pcdCommon.centerCamPoint, leftPoint, midPoint)
    angleRight = pcdCommon.getAngleRadians(pcdCommon.centerCamPoint, midPoint, rightPoint)
    angleLeft = angleLeft * (180 / math.pi)
    angleRight = angleRight * (180 / math.pi)
    
    # Rotate the halves of the shadow
    replaceLeftShadow = pcdCommon.rotatePoints(replaceLeftShadow, 360 - angleLeft)
    replaceRightShadow = pcdCommon.rotatePoints(replaceRightShadow, angleRight)

    # Convert shadow halves to masks
    pcdCastHull = o3d.geometry.PointCloud()
    pcdCastHull.points = o3d.utility.Vector3dVector(replaceLeftShadow)
    shadowRotated, _ = pcdCastHull.compute_convex_hull()
    pcdCastHull = o3d.geometry.PointCloud()
    pcdCastHull.points = o3d.utility.Vector3dVector(replaceRightShadow)
    shadowRotated2, _ = pcdCastHull.compute_convex_hull()

    # Get points included within the halves of the shadow
    maskIncluded = pcdCommon.checkInclusionBasedOnTriangleMesh(scene, shadowRotated)
    pcdIncluded = scene[maskIncluded]
    intensityIncluded = intensity[maskIncluded]
    semanticsIncluded = semantics[maskIncluded]
    instancesIncluded = instances[maskIncluded]
    maskIncluded2 = pcdCommon.checkInclusionBasedOnTriangleMesh(scene, shadowRotated2)
    pcdIncluded2 = scene[maskIncluded2]
    intensityIncluded2 = intensity[maskIncluded2]
    semanticsIncluded2 = semantics[maskIncluded2]
    instancesIncluded2 = instances[maskIncluded2]


    # Validate that the points don't include any semantic types that can't be used in a replacement
    # This prevents situations with half cars being copied
    semSetInval = set()
    for sem in semanticsIncluded:
        if (sem in semanticMapping.instancesVehicle.keys()
            or sem in semanticMapping.instancesWalls.keys()):
            semSetInval.add(sem)
    for sem in semanticsIncluded2:
        if (sem in semanticMapping.instancesVehicle.keys()
            or sem in semanticMapping.instancesWalls.keys()):
            semSetInval.add(sem)
    
    if (len(semSetInval) > 0):
        invalidSem = ""
        for sem in semSetInval:
            invalidSem += (semanticMapping.name_label_mapping[sem] + " ")
        # print("Invalid semantics to replace with: {}".format(invalidSem))
        details["issue"] = "Invalid semantics to replace with: {}".format(invalidSem)
        return False, None, None, None, None, details, None


    # Rotate any points included in the shadow halves to fill the hole
    if (len(pcdIncluded) > 0):
        pcdIncluded = pcdCommon.rotatePoints(pcdIncluded, angleLeft)
    else:
        # print("left points empty")
        details["issue"] = "left points empty"
    if (len(pcdIncluded2) > 0):
        pcdIncluded2 = pcdCommon.rotatePoints(pcdIncluded2, 360 - angleRight)
    else:
        # print("right points empty")
        details["issue"] = "right points empty"

    # Combine the left and right replacement points
    pcdIncluded, intensityIncluded, semanticsIncluded, instancesIncluded = pcdCommon.combine(pcdIncluded, intensityIncluded, semanticsIncluded, instancesIncluded,
                                                                                        pcdIncluded2, intensityIncluded2, semanticsIncluded2, instancesIncluded2)

    # # -----------------------
    # # Visualization for REMOVE, for debugging 
    # hull_ls = o3d.geometry.LineSet.create_from_triangle_mesh(shadow)
    # hull_ls.paint_uniform_color((0, 0.5, 1))
    # hull_ls2 = o3d.geometry.LineSet.create_from_triangle_mesh(shadowRotated)
    # hull_ls2.paint_uniform_color((0, 1, 0.5))
    # hull_ls22 = o3d.geometry.LineSet.create_from_triangle_mesh(shadowRotated2)
    # hull_ls22.paint_uniform_color((1, 0, 0.5))

    # pcdNewAddition = o3d.geometry.PointCloud()
    # pcdNewAddition.points = o3d.utility.Vector3dVector(pcdIncluded)
    # pcdScene = o3d.geometry.PointCloud()
    # pcdScene.points = o3d.utility.Vector3dVector(scene)

    # pcdCast2 = o3d.geometry.PointCloud()
    # pcdCast2.points = o3d.utility.Vector3dVector(np.asarray([rightPoint, leftPoint, midPointMinZ, midPointMaxZ, midPoint]))
    # pcdCast2.paint_uniform_color((.6, 0, .6))

    # o3d.visualization.draw_geometries([hull_ls, hull_ls2, hull_ls22, pcdNewAddition, pcdScene, pcdCast2])
    # # -----------------------


    # Combine the new points with the scene to fill the asset's hole
    sceneReplace, intensityReplace, semanticsReplace, instancesReplace = pcdCommon.combine(pcdIncluded, intensityIncluded, semanticsIncluded, instancesIncluded,
                                                                                            scene, intensity, semantics, instances)

    # Update model prediction files
    for model in modelPredictions.keys():
        modelSem1 = modelPredictions[model][maskIncluded]
        modelSem2 = modelPredictions[model][maskIncluded2]
        semanticsCombinedHole = np.hstack((modelSem1, modelSem2))
        semanticsCombined = np.hstack((semanticsCombinedHole, modelPredictions[model]))
        modelPredictions[model] = semanticsCombined
        
    # Note how many points were utilized in this mutation
    details["pointsRemoved"] = int(np.shape(asset)[0])
    details["pointsAdded"] = len(pcdIncluded) + len(pcdIncluded2)
    details["pointsAffected"] = int(np.shape(asset)[0]) + len(pcdIncluded) + len(pcdIncluded2)

    return True, sceneReplace, intensityReplace, semanticsReplace, instancesReplace, details, modelPredictions





