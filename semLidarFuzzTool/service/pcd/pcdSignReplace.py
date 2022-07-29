"""
pcdSignReplace
Sign Replace Mutation

@Date 6/23/22
"""


import copy
from enum import Enum
import numpy as np
import open3d as o3d
import random
import sys

import service.pcd.pcdCommon as pcdCommon
import domain.config as config


# --------------------------------------------------------------------------

# Enum of the different types of sign replacements
class Signs(Enum):
    YEILD = "YEILD",
    CROSSBUCK = "CROSSBUCK",
    WARNING = "WARNING",
    SPEED = "SPEED",
    STOP = "STOP",


# --------------------------------------------------------------------------
# Sign Change


"""
signReplace

Replaces a sign with a different sign type
"""
def signReplace(signAsset, intensityAsset, semanticsAsset, instancesAsset, 
                scene, intensity, semantics, instances, 
                details, signType,
                modelPredictionsScene, modelPredictionsAsset):

    # Add pole to scene model predictions
    for model in modelPredictionsAsset.keys():
        modelPole = modelPredictionsAsset[model][semanticsAsset == 80]
        modelPredictionsScene[model] = np.hstack((modelPredictionsScene[model], modelPole))
        modelPredictionsAsset[model] = modelPredictionsAsset[model][semanticsAsset == 81]

    # Seperate the two portions of a tagged sign
    pole = signAsset[semanticsAsset == 80]
    intensityPole = intensityAsset[semanticsAsset == 80]
    semanticsPole = semanticsAsset[semanticsAsset == 80]
    instancesPole = instancesAsset[semanticsAsset == 80]
    sign = signAsset[semanticsAsset == 81]
    intensitySign = intensityAsset[semanticsAsset == 81]
    semanticsSign = semanticsAsset[semanticsAsset == 81]
    instancesSign = instancesAsset[semanticsAsset == 81]

    # Validate that there are enough points to make a hull from (5)
    if (np.shape(pole)[0] < config.SIGN_MIN_POLE_POINTS or np.shape(sign)[0] < config.SIGN_MIN_SIGN_POINTS):
        details["issue"] = "Sign {} pole {}, too little points".format(np.shape(sign)[0], np.shape(pole)[0])
        return False, (None, None, None, None), (None, None, None, None), details, None, None
    
    # Get the bounding box for both the sign and pole
    pcdSign = o3d.geometry.PointCloud()
    pcdSign.points = o3d.utility.Vector3dVector(sign)

    pcdPole = o3d.geometry.PointCloud()
    pcdPole.points = o3d.utility.Vector3dVector(pole)
    poleBox = pcdPole.get_oriented_bounding_box()

    # Center the new sign on the pole
    signCenter = poleBox.get_center()
    
    # Get bounds to align the sign to 
    hull, _ = pcdSign.compute_convex_hull()
    minSign, maxSign = pcdCommon.getLeftAndRightEdges(hull)

    minZSign = sys.maxsize
    for point in sign:
        minZSign = min(minZSign, point[2])

    maxSign[2] = minZSign
    minSign[2] = minZSign
    signCenter[2] = minZSign
    signLen = np.linalg.norm(maxSign - minSign)

    # Create mesh of new sign
    signMesh, details = getSignMesh(details, signType)

    # Get the bounds and height of the current sign
    meshMin = signMesh.get_min_bound()
    meshMax = signMesh.get_max_bound()
    heightMesh = meshMax[2] - meshMin[2]
    meshMax[2] = minZSign
    meshMin[2] = minZSign
    
    # Validate that the sign is not too low to the ground
    if (minZSign < config.SIGN_MIN_ALLOWED_SIGN_HEIGHT): # (-1)
        details["issue"] = "Sign too low min {}".format(minZSign)
        return False, (None, None, None, None), (None, None, None, None), details, None, None

    # Validate that the og sign and new sign are roughly the same size
    meshLen = np.linalg.norm(meshMin - meshMin)
    if (np.absolute(meshLen - signLen) > config.SIGN_SIZE_CHECK): # (2)
        details["issue"] = "Distance to sign too great: mesh len {}, sign len {}".format(meshLen, signLen)
        return False, (None, None, None, None), (None, None, None, None), details, None, None


    # Move the mesh to new location based on: pole center, original sign min, and height of the new sign
    signCenter[2] = minZSign + (heightMesh / 2) 
    signMesh.translate(signCenter, relative=False)
    angleSign = pcdCommon.getAngleRadians(signCenter, minSign, signMesh.get_min_bound())

    # Get two rotation options to match the original sign
    rotation = signMesh.get_rotation_matrix_from_xyz((0, 0, angleSign * -1))
    rotation2 = signMesh.get_rotation_matrix_from_xyz((0, 0, angleSign))
    signMeshRotate1 = copy.deepcopy(signMesh)
    signMeshRotate2 = copy.deepcopy(signMesh)
    signMeshRotate1.rotate(rotation, center=signMeshRotate1.get_center())
    signMeshRotate2.rotate(rotation2, center=signMeshRotate2.get_center())

    # Get the rotation that is closer to the original sign's angle 
    dist1 = np.linalg.norm(minSign - signMeshRotate1.get_min_bound())
    dist2 = np.linalg.norm(minSign - signMeshRotate2.get_min_bound())
    if (dist1 < dist2):
        signMesh = signMeshRotate1
    else:
        signMesh = signMeshRotate2


    # Add the pole points to the scene
    scene, intensity, semantics, instances = pcdCommon.combine(scene, intensity, semantics, instances, 
                                                    pole, intensityPole, semanticsPole, instancesPole)


    # Pull the points in the scene to the new sign mesh
    assetData = (sign, intensitySign, semanticsSign, instancesSign)
    sceneData = (scene, intensity, semantics, instances)
    success, newAssetData, newSceneData, details, modelPredictionsScene, modelPredictionsAsset = pointsToMesh(signMesh, assetData, sceneData, details, modelPredictionsScene, modelPredictionsAsset)

    # sign, intensitySign, semanticsSign, instancesSign = newAssetData

    # Validate that the sign has points (min 15)
    if (success and np.shape(newAssetData[0])[0] < config.SIGN_MIN_POINTS):
        # print("Sign too little points")
        details["issue"] = "Sign too little points {}".format(np.shape(sign)[0])
        success = False


    return success, newSceneData, newAssetData, details, modelPredictionsScene, modelPredictionsAsset



"""
getSignMesh

Creates a mesh of the sign size
"""
def getSignMesh(details, signType):

    # Either randomly select sign type or use given sign type
    sign = signType
    if (not signType):
        sign = random.choice(list(Signs))
        sign = sign.name
    signMesh = None

    if (Signs.SPEED.name == sign):

        signMesh = o3d.geometry.TriangleMesh.create_box(width=0.05, height=0.6, depth=0.75)

    elif (Signs.STOP.name == sign):

        # Create mesh
        box = o3d.geometry.TriangleMesh.create_box(width=0.05, height=0.75, depth=0.30)
        box2 = o3d.geometry.TriangleMesh.create_box(width=0.05, height=0.30, depth=0.75)

        # Center on top of eachother
        box.translate([0, 0, 0], relative=False)
        box2.translate([0, 0, 0], relative=False)

        # Combine vertices
        signVertices = np.vstack((np.array(box.vertices), np.array(box2.vertices)))
        pcdSign = o3d.geometry.PointCloud()
        pcdSign.points = o3d.utility.Vector3dVector(signVertices)

        #  Get the asset's hull mesh
        signMesh, _ = pcdSign.compute_convex_hull()

    elif (Signs.CROSSBUCK.name == sign):

        # Create mesh
        box = o3d.geometry.TriangleMesh.create_box(width=0.05, height=0.22, depth=1.22)
        box2 = o3d.geometry.TriangleMesh.create_box(width=0.05, height=1.22, depth=0.22)

        # Center on top of each other combine
        box.translate([0, 0, 0], relative=False)
        box2.translate([0, 0, 0], relative=False)
        signMesh = box + box2

        # Rotate 45 degrees
        radiansRotation = (45 * np.pi) / 180
        rotation2 = signMesh.get_rotation_matrix_from_xyz((radiansRotation, 0, 0))
        signMesh.rotate(rotation2, center=box.get_center())

    elif (Signs.WARNING.name == sign):

        signMesh = o3d.geometry.TriangleMesh.create_box(width=0.05, height=0.76, depth=0.76)

        # Rotate 45 degrees
        radiansRotation = (45 * np.pi) / 180    
        rotation = signMesh.get_rotation_matrix_from_xyz((radiansRotation, 0, 0))
        signMesh.rotate(rotation, center=signMesh.get_center())
        
    elif (Signs.YEILD.name == sign):

        # Define points for yeild sign
        yeildPoints = np.array([[0, -0.455, 0.91], 
                            [0, 0, 0.91], 
                            [0, 0.455, 0.91], 
                            [0, 0, 0],
                            [0.05, -0.455, 0.91], 
                            [0.05, 0, 0.91], 
                            [0.05, 0.455, 0.91], 
                            [0.05, 0, 0]])

        pcdSign = o3d.geometry.PointCloud()
        pcdSign.points = o3d.utility.Vector3dVector(yeildPoints)

        #  Get the asset's hull mesh
        signMesh, _ = pcdSign.compute_convex_hull()

    else: 
        print("Sign type {} not supported".format(sign))

    signName = str(sign)
    details["sign"] = signName

    return signMesh, details





"""
pointsToMesh

Moves the points from the asset and scene to the sign mesh
Taking closest intensity from the asset
"""
def pointsToMesh(mesh, assetData, sceneData, details, modelPredictionsScene, modelPredictionsAsset):

    asset, intensityAsset, semanticsAsset, instancesAsset = assetData
    scene, intensity, semantics, instances = sceneData

    # http://www.open3d.org/docs/latest/tutorial/geometry/ray_casting.html
    # Calulate intersection for scene to mesh points
    legacyMesh = o3d.t.geometry.TriangleMesh.from_legacy(mesh)
    sceneRays = o3d.t.geometry.RaycastingScene()
    sceneRays.add_triangles(legacyMesh)

    if (np.shape(scene)[0] < 1 or np.shape(asset)[0] < 1):
        # print("SCENE or ASSET PROVIDED EMPTY: SCENE {}, ASSET {}".format(np.shape(scene)[0], np.shape(asset)[0]))
        details["issue"] = "SCENE or ASSET PROVIDED EMPTY: SCENE {}, ASSET {}".format(np.shape(scene)[0], np.shape(asset)[0])
        return False, (None, None, None, None), (None, None, None, None), details, None, None

    raysVectorsScene = []
    for point in scene:
        raysVectorsScene.append([0, 0, 0, point[0], point[1], point[2]])

    rays = o3d.core.Tensor(raysVectorsScene, dtype=o3d.core.Dtype.Float32)
    ans = sceneRays.cast_rays(rays)
    hit = ans['t_hit'].isfinite()
    pointsOnMesh = rays[hit][:,:3] + rays[hit][:,3:]*ans['t_hit'][hit].reshape((-1,1))

    # Split between intersect and non intersect
    intensityIntersect = intensity[hit.numpy()]
    semanticsIntersect = semantics[hit.numpy()]
    instancesIntersect = instances[hit.numpy()]
    nonHit = np.logical_not(hit.numpy())
    sceneNonIntersect = scene[nonHit]
    intensityNonIntersect = intensity[nonHit]
    semanticsNonIntersect = semantics[nonHit]
    instancesNonIntersect = instances[nonHit]
    
    newAssetScene = []
    for vector in pointsOnMesh:
        newAssetScene.append(vector.numpy())

    # Calulate intersection for sign points
    raysVectorsMesh = []
    for point in asset:
        raysVectorsMesh.append([0, 0, 0, point[0], point[1], point[2]])

    rays = o3d.core.Tensor(raysVectorsMesh, dtype=o3d.core.Dtype.Float32)
    ans = sceneRays.cast_rays(rays)
    hitAsset = ans['t_hit'].isfinite()
    pointsOnMesh = rays[hitAsset][:,:3] + rays[hitAsset][:,3:]*ans['t_hit'][hitAsset].reshape((-1,1))

    newAsset = []
    for vector in pointsOnMesh:
        newAsset.append(vector.numpy())
    
    intensityAsset = intensityAsset[hitAsset.numpy()] 
    semanticsAsset = semanticsAsset[hitAsset.numpy()]
    instancesAsset = instancesAsset[hitAsset.numpy()]
    nonHitAsset = np.logical_not(hitAsset.numpy())

    if len(newAsset) == 0 or len(newAssetScene) == 0:
        details["issue"] = "GOT NONE OF THE ORIGINAL ASSET {} OR NONE OF SCENE {}".format(len(newAsset), len(newAssetScene))
        return False, (None, None, None, None), (None, None, None, None), details, None, None


    # Update the model prediction semantics as we go
    modelsSemIntersect = {}
    for model in modelPredictionsAsset.keys():
        # Add pole to scene 
        modelPredictionsAsset[model]
        modelsSemIntersect[model] = modelPredictionsScene[model][hit.numpy()]


    # Fix the intensity of each of the points in the scene that were pulled into the sign by using the closest sign point
    pcdAssetNearest = o3d.geometry.PointCloud()
    pcdAssetNearest.points = o3d.utility.Vector3dVector(newAsset)
    pcd_tree = o3d.geometry.KDTreeFlann(pcdAssetNearest)
    for pointIndex in range(0, len(newAssetScene)):
        [k, idx, _] = pcd_tree.search_knn_vector_3d(newAssetScene[pointIndex], 1)
        intensityIntersect[pointIndex] = intensityAsset[idx]
        semanticsIntersect[pointIndex] = semanticsAsset[idx]
        instancesIntersect[pointIndex] = instancesAsset[idx]

        # Update model pred
        for model in modelPredictionsAsset.keys():
            modelsSemIntersect[model][pointIndex] = modelPredictionsAsset[model][idx]

    # Combine the original points of the asset and the new scene points
    newAsset, intensityAsset, semanticsAsset, instancesAsset = pcdCommon.combine(newAsset, intensityAsset, semanticsAsset, instancesAsset, 
                                                                    newAssetScene, intensityIntersect, semanticsIntersect, instancesIntersect)


    # Update model pred semantics
    for model in modelPredictionsAsset.keys():
        # Update Asset
        newSemanticsAssetModel = modelPredictionsAsset[model][hitAsset.numpy()]
        modelPredictionsAsset[model] = np.hstack((newSemanticsAssetModel, modelsSemIntersect[model]))
        # Update Scene
        modelPredictionsScene[model] = modelPredictionsScene[model][nonHit]


    # Update point metrics
    details["pointsRemoved"] = int(np.sum(nonHitAsset))
    details["pointsMoved"] = int(np.shape(newAsset)[0])
    details["pointsAffected"] = int(np.shape(newAsset)[0]) + int(np.sum(nonHitAsset))

    # Return revised scene
    newAssetData = (newAsset, intensityAsset, semanticsAsset, instancesAsset)
    newSceneData = (sceneNonIntersect, intensityNonIntersect, semanticsNonIntersect, instancesNonIntersect)
    return True, newAssetData, newSceneData, details, modelPredictionsScene, modelPredictionsAsset




