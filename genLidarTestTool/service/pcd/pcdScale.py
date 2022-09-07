"""
pcdScale
Scale Mutation

@Date 6/23/22
"""


import copy
import numpy as np
import open3d as o3d

import service.pcd.pcdCommon as pcdCommon
import domain.config as config


# --------------------------------------------------------------------------
# Scale


"""
scaleVehicle

Scales a vehicle by creating a mesh, 
Scaling that mesh
Then calculating the intersection of points behind that mesh
"""
def scaleVehicle(asset, intensityAsset, semanticsAsset, instancesAsset, 
                scene, intensity, semantics, instances, details, scaleAmount,
                modelPredictionsScene, modelPredictionsAsset):


    # Prepare to create the mesh estimating normals
    pcdAsset = o3d.geometry.PointCloud()
    pcdAsset.points = o3d.utility.Vector3dVector(asset)
    pcdAsset.estimate_normals()
    pcdAsset.orient_normals_towards_camera_location()

    
    # Check if count of points are greater than allowed to use ball pivoting on (10000)
    # Larger point counts take longer for this to run
    if (np.shape(asset)[0] > config.SCALE_MESH_POINTS_THRESHOLD):
        details["issue"] = "Point count {} exceeds scale point limit {}".format(np.shape(asset)[0], config.SCALE_MESH_POINTS_THRESHOLD)
        return False, (None, None, None, None), (None, None, None, None), details, None, None
    
    # Create a mesh using the ball pivoting method radii(0.15)
    radii = [config.SCALE_MESH_RADII]
    mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(pcdAsset, o3d.utility.DoubleVector(radii))

    # o3d.visualization.draw_geometries([mesh])

    # Check that the mesh is valid
    if (np.shape(np.array(mesh.vertices))[0] < 1 or np.shape(np.array(mesh.triangles))[0] < 1):
        # print("MESH NOT SUFFICENT: Vertices {} Triangles {}".format(np.shape(np.array(mesh.vertices))[0], np.shape(np.array(mesh.triangles))[0]))
        details["issue"] = "MESH NOT SUFFICENT: Vertices {} Triangles {}".format(np.shape(np.array(mesh.vertices))[0], np.shape(np.array(mesh.triangles))[0])
        return False, (None, None, None, None), (None, None, None, None), details, None, None
    
    # Smooth the mesh
    mesh = mesh.filter_smooth_simple(number_of_iterations=1)
    mesh.compute_vertex_normals()

    # Scale the vehicle mesh
    scale = scaleAmount
    if (not scale):
        # scale = random.uniform(1.01, 1.05)
        scale = config.SCALE_AMOUNT
    details["scale"] = scale
    mesh.scale(scale, center=mesh.get_center())

    # Scale the points to use later for intensity 
    scaledPoints = copy.deepcopy(pcdAsset).scale(scale, center=mesh.get_center())

    # http://www.open3d.org/docs/latest/tutorial/geometry/ray_casting.html
    # Calulate intersection for scene to mesh points
    legacyMesh = o3d.t.geometry.TriangleMesh.from_legacy(mesh)
    sceneRays = o3d.t.geometry.RaycastingScene()
    sceneRays.add_triangles(legacyMesh)

    if (np.shape(scene)[0] < 1 or np.shape(asset)[0] < 1):
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
    
    newIntensityAsset = intensityAsset[hitAsset.numpy()] 
    newSemanticsAsset = semanticsAsset[hitAsset.numpy()]
    newInstancesAsset = instancesAsset[hitAsset.numpy()]
    nonHitAsset = np.logical_not(hitAsset.numpy())

    # print(len(newAsset))
    # print(len(newAssetScene))

    if len(newAsset) == 0 or len(newAssetScene) == 0:
        details["issue"] = "GOT NONE OF THE OG ASSET {} OR NONE OF SCENE {}".format(len(newAsset), len(newAssetScene))
        return False, (None, None, None, None), (None, None, None, None), details, None, None

    
    # Update the model prediction semantics as we go
    modelsSemIntersect = {}
    for model in modelPredictionsScene.keys():
        modelsSemIntersect[model] = modelPredictionsScene[model][hit.numpy()]


    # Fix the intensity of each of the points in the scene that were pulled into the asset by using the closest scaled asset point
    pcd_tree = o3d.geometry.KDTreeFlann(scaledPoints)
    for pointIndex in range(0, len(newAssetScene)):
        [k, idx, _] = pcd_tree.search_knn_vector_3d(newAssetScene[pointIndex], 1)
        intensityIntersect[pointIndex] = intensityAsset[idx]
        semanticsIntersect[pointIndex] = semanticsAsset[idx]
        instancesIntersect[pointIndex] = instancesAsset[idx]

        # Update model pred
        for model in modelPredictionsAsset.keys():
            modelsSemIntersect[model][pointIndex] = modelPredictionsAsset[model][idx]

    newAsset, intensityAsset, semanticsAsset, instancesAsset = pcdCommon.combine(newAsset, newIntensityAsset, newSemanticsAsset, newInstancesAsset, 
                                                                    newAssetScene, intensityIntersect, semanticsIntersect, instancesIntersect)


    # Check that we have some points after the transformation (20)
    if (np.shape(newAsset)[0] < config.SCALE_MIN_POINTS):
        details["issue"] = "New asset too little points {}".format(np.shape(newAsset)[0])
        return False, (None, None, None, None), (None, None, None, None), details, None, None


    # Update model pred semantics
    for model in modelPredictionsAsset.keys():
        # Update Asset
        newSemanticsAssetModel = modelPredictionsAsset[model][hitAsset.numpy()]
        modelPredictionsAsset[model] = np.hstack((newSemanticsAssetModel, modelsSemIntersect[model]))
        # Update Scene
        modelPredictionsScene[model] = modelPredictionsScene[model][nonHit]


    # Update the points affected
    details["pointsRemoved"] = int(np.sum(nonHitAsset))
    details["pointsAffected"] = int(np.shape(newAsset)[0])

    resultAsset = (newAsset, intensityAsset, semanticsAsset, instancesAsset)
    resultScene = (sceneNonIntersect, intensityNonIntersect, semanticsNonIntersect, instancesNonIntersect)

    # Return revised scene with scaled vehicle 
    return True, resultAsset, resultScene, details, modelPredictionsScene, modelPredictionsAsset
















