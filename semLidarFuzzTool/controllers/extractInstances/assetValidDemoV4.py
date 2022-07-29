

from pymongo import MongoClient
import glob, os
import numpy as np
import open3d as o3d
import math
import random
import argparse
import sys


# sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../..")
import service.pcd.pcdCommon as pcdCommon


# ------------------------------------------------------------------


color_map_alt = { # rgb
#   0 : [0, 0, 0],
  0 : [220, 220, 220],
  1 : [0, 0, 0],
  10: [100, 150, 245],
  11: [100, 230, 245],
  13: [0, 0, 255],
  15: [30, 60, 150],
  16: [0, 0, 255],
  18: [80, 30, 180],
  20: [0, 0, 255],
  30: [255, 30, 30],
  31: [255, 40, 200],
  32: [150, 30, 90],
  40: [255, 0, 255],
  44: [255, 150, 255],
  48: [75, 0, 75],
  49: [175, 0, 75],
  50: [255, 200, 0],
  51: [255, 120, 50],
  52: [0, 0, 0],
  60: [255, 0, 255],
  70: [0, 175, 0],
  71: [135, 60, 0],
  72: [150, 240, 80],
  80: [255, 240, 150],
  81: [255, 0, 0],
  99: [0, 0, 0],
  252: [100, 150, 245],
  253: [255, 40, 200],
  254: [255, 30, 30],
  255: [150, 30, 90],
  256: [0, 0, 255],
  257: [0, 0, 255],
  258: [80, 30, 180],
  259: [0, 0, 255],
}

centerCamPoint = np.array([0, 0, 0.3])

# ------------------------------------------------------------------

def getDistDisplay(dist):
    
    circle = []
    point = [dist, 0]

    for angle in range(0, 360):
        x, y = pcdCommon.rotateOnePoint([0, 0], point, angle)

        circle.append([x, y, 0])

    return np.array(circle)


def checkInclusionBasedOnTriangleMeshAsset(points, mesh):

    obb = mesh.get_oriented_bounding_box()

    legacyMesh = o3d.t.geometry.TriangleMesh.from_legacy(mesh)

    scene = o3d.t.geometry.RaycastingScene()
    _ = scene.add_triangles(legacyMesh)

    pointsVector = o3d.utility.Vector3dVector(points)

    indexesWithinBox = obb.get_point_indices_within_bounding_box(pointsVector)
    
    for idx in indexesWithinBox:
        pt = points[idx]
        query_point = o3d.core.Tensor([pt], dtype=o3d.core.Dtype.Float32)

        occupancy = scene.compute_occupancy(query_point)
        if (occupancy == 1): 
            # foundNum += 1
            # if (foundNum >= acceptableNum):
            return True

    return False


def assetIsValid(asset, sceneWithoutInstance, semanticsWithoutInstance):

    pcdAsset = o3d.geometry.PointCloud()
    pcdAsset.points = o3d.utility.Vector3dVector(asset)

    #  Get the asset's bounding box
    obb = pcdAsset.get_oriented_bounding_box()
    assetCenter = obb.get_center()
    dist = np.linalg.norm(centerCamPoint - assetCenter)

    scalingFactor = (dist / 150) + 1
    print("Scaling {} Distance {}".format(scalingFactor, dist))
    obb.scale(scalingFactor, assetCenter)

    boxPoints = np.asarray(obb.get_box_points())

    boxPoints = boxPoints[boxPoints[:, 2].argsort()]
    boxPoints[:2, 2] -= 5
    # boxPoints[6:, 2] += 15
    

    boxVertices = np.vstack((boxPoints, centerCamPoint))

    pcdCastHull = o3d.geometry.PointCloud()
    pcdCastHull.points = o3d.utility.Vector3dVector(boxVertices)
    hull2, _ = pcdCastHull.compute_convex_hull()
    hull_ls = o3d.geometry.LineSet.create_from_triangle_mesh(hull2)
    



    # Dist is acceptable
    if dist > 40:
        hull_ls.paint_uniform_color((1, 0.4, 0.2))
        return hull_ls, False

    
    incuded = checkInclusionBasedOnTriangleMeshAsset(sceneWithoutInstance, hull2)
    if (incuded):
        hull_ls.paint_uniform_color((1, 0.2, 0.2))
    else:
        hull_ls.paint_uniform_color((0.2, 1, 0.2))

    return hull_ls, not incuded


def removeLidarShadowLines(asset):

    # Prepare asset and scene point clouds
    pcdAsset = o3d.geometry.PointCloud()
    pcdAsset.points = o3d.utility.Vector3dVector(asset)

    #  Get the asset's hull mesh
    hull, _ = pcdAsset.compute_convex_hull()
    hullVertices = np.asarray(hull.vertices)
    
    castHullPoints = np.array([])
    for point1 in hullVertices:

        ba = centerCamPoint - point1
        baLen = math.sqrt((ba[0] * ba[0]) + (ba[1] * ba[1]) + (ba[2] * ba[2]))
        ba2 = ba / baLen

        pt2 = centerCamPoint + ((-100) * ba2)

        if (np.size(castHullPoints)):
            castHullPoints = np.vstack((castHullPoints, [pt2]))
        else:
            castHullPoints = np.array([pt2])

    pcdCastHull = o3d.geometry.PointCloud()
    pcdCastHull.points = o3d.utility.Vector3dVector(castHullPoints)
    hull2, _ = pcdCastHull.compute_convex_hull()

    hull2Vertices = np.asarray(hull2.vertices)

    combinedVertices = np.vstack((hullVertices, hull2Vertices))

    pcdCut = o3d.geometry.PointCloud()
    pcdCut.points = o3d.utility.Vector3dVector(combinedVertices) 
    cutPointsHull, _ = pcdCut.compute_convex_hull()
    hull_ls = o3d.geometry.LineSet.create_from_triangle_mesh(cutPointsHull)
    hull_ls.paint_uniform_color((0, 1, 1))

    return hull_ls



def addSignInstances(scene, semantics, instances):
    
    uniqueInst = set()
    for instance in instances:
        uniqueInst.add(instance)

    maskSign = (semantics == 81) | (semantics == 80)

    onlySigns = scene[maskSign, :]
    semanticsSigns = semantics[maskSign]

    indexesSignMask = np.where(maskSign)

    # Check that there are signs 
    if (np.shape(onlySigns)[0] < 1):
        print("NO SIGNS FOUND")
        return instances

    pcdSigns = o3d.geometry.PointCloud()
    pcdSigns.points = o3d.utility.Vector3dVector(onlySigns)

    labels = np.array(pcdSigns.cluster_dbscan(eps=2, min_points=10, print_progress=True))
    max_label = labels.max()
    print(f"point cloud has {max_label + 1} clusters")

    if (max_label < 0):
        print("NO SIGNS FOUND")
        return instances

    uniqueLabels = {}
    uniqueSeenLabels = set()
    for labelNum in labels:
        if (labelNum != -1 and # outliers
            labelNum not in uniqueSeenLabels): # already relabeled
            
            uniqueSeenLabels.add(labelNum)

            semanticsSign = semanticsSigns[labels == labelNum]

            types = set()
            for sem in semanticsSign:
                types.add(sem)

            if (len(types) > 1):

                pointsSign = onlySigns[labels == labelNum]
                pcdSign = o3d.geometry.PointCloud()
                pcdSign.points = o3d.utility.Vector3dVector(pointsSign)
                obb = pcdSign.get_oriented_bounding_box()
                maxXy = obb.get_max_bound()
                minXy = obb.get_min_bound()
                maxXy[2] = 0
                minXy[2] = 0
                distAcross = np.linalg.norm(maxXy - minXy)

                print("Sign across: {}".format(distAcross))

                if (distAcross < 3):

                    newLabel = 0
                    while (newLabel < 10):
                        randInstLabel = random.randint(1000, 2000)
                        if (randInstLabel not in uniqueInst):
                            uniqueLabels[labelNum] = randInstLabel
                            uniqueInst.add(randInstLabel)
                            newLabel = randInstLabel
                        else:
                            newLabel += 1

        



    for sign in uniqueLabels.keys():
        # print(indexesSignMask)
        # print(np.shape(indexesSignMask))
        # print(np.shape(labels))
        # print(sign)
        # print(labels)
        currentSignIndexes = indexesSignMask[0][labels == sign]
        instances[currentSignIndexes] = uniqueLabels[sign]


    return instances





def viewOne(binFileName, labelsFileName):
    print(binFileName)
    print(labelsFileName)

    # Label
    label_arr = np.fromfile(labelsFileName, dtype=np.int32)
    semantics = label_arr & 0xFFFF
    instances = label_arr >> 16 

    # Bin File
    pcdArr = np.fromfile(binFileName, dtype=np.float32)
    pcdArr = pcdArr.reshape((int(np.shape(pcdArr)[0]) // 4, 4))
    pcdArr = np.delete(pcdArr, 3, 1)


    # Extract signs
    instances = addSignInstances(pcdArr, semantics, instances)



    seenInst = set()
    for instance in instances:
        seenInst.add(instance)
    
    pcdScene = o3d.geometry.PointCloud()
    pcdScene.points = o3d.utility.Vector3dVector(pcdArr)

    # color scene with semantics
    colors = np.zeros(np.shape(pcdArr), dtype=np.float64)
    for semIdx in range(0, len(semantics)):
        colors[semIdx][0] = (color_map_alt[semantics[semIdx]][0] / 255)
        colors[semIdx][1] = (color_map_alt[semantics[semIdx]][1] / 255)
        colors[semIdx][2] = (color_map_alt[semantics[semIdx]][2] / 255)
    pcdScene.colors = o3d.utility.Vector3dVector(colors)
        

    # mask1 = (semantics != 40) & (semantics != 44) & (semantics != 48) & (semantics != 49) & (semantics != 60) & (semantics != 72)
    # tmp = pcdArr[mask1, :]
    # pcdScene = o3d.geometry.PointCloud()
    # pcdScene.points = o3d.utility.Vector3dVector(tmp)

    display = [pcdScene]

    # Box for center points
    centerArea = np.array([
            [ -2.5, -2.5, -2], # bottom right
            [ -2.5, -2.5, 3], 
            [ -2.5, 2.5, -2], # top right
            [ -2.5, 2.5, 3],
            [ 2.5, 2.5, -2], # top left
            [ 2.5, 2.5, 3],
            [ 2.5, -2.5, -2], # bottom left
            [ 2.5, -2.5, 3], 
            ]).astype("float64")
    
    pcdCenter = o3d.geometry.PointCloud()
    pcdCenter.points = o3d.utility.Vector3dVector(centerArea)

    #  Get the asset's bounding box
    centerBox = pcdCenter.get_oriented_bounding_box()
    centerBox.color = (0.1, 0.2, 0.2)
    display.append(centerBox)

    for instance in seenInst:
        if instance != 0:
            instancePoints = pcdArr[instances == instance]
            instanceSemantics = semantics[instances == instance]

            if (np.shape(instancePoints)[0] > 20):
                pcdItem = o3d.geometry.PointCloud()
                pcdItem.points = o3d.utility.Vector3dVector(instancePoints)
                hull, _ = pcdItem.compute_convex_hull()
                hull_ls = o3d.geometry.LineSet.create_from_triangle_mesh(hull)
                hull_ls.paint_uniform_color((0, 0, 1))


                maskInst = (instances != instance) & (semantics != 0) & (semantics != 1) & (semantics != 40) & (semantics != 44) & (semantics != 48) & (semantics != 49) & (semantics != 60) & (semantics != 72)
                pcdWithoutInstance = pcdArr[maskInst, :]
                semanticsWithoutInstance = semantics[maskInst]

                boxToVel, valid = assetIsValid(instancePoints, pcdWithoutInstance, semanticsWithoutInstance)
                

                display.append(hull_ls)
                if (valid):
                    display.append(removeLidarShadowLines(instancePoints))
                    display.append(boxToVel)
                    # display.append(hullToVelLines(instancePoints, pcdWithoutInstance))
                else:
                    display.append(boxToVel)

                # get_oriented_bounding_box
                # get_axis_aligned_bounding_box
                # obb = pcdItem.get_oriented_bounding_box()
                # obb.color = (0.7, 0, 1)
                # display.append(obb)
                
                # if (valid):
                #     colors = np.zeros(np.shape(instancePoints), dtype=np.float64)
                #     for semIdx in range(0, len(instancePoints)):
                #         colors[semIdx][0] = (color_map_alt[instanceSemantics[semIdx]][0] / 255)
                #         colors[semIdx][1] = (color_map_alt[instanceSemantics[semIdx]][1] / 255)
                #         colors[semIdx][2] = (color_map_alt[instanceSemantics[semIdx]][2] / 255)
                #     pcdItem.colors = o3d.utility.Vector3dVector(colors)
                #     o3d.visualization.draw_geometries([pcdItem, boxToVel])

    circle = getDistDisplay(40)
    pcdCircle = o3d.geometry.PointCloud()
    pcdCircle.points = o3d.utility.Vector3dVector(circle)
    pcdCircle.paint_uniform_color([0.57, 0.67, 0.67])
    display.append(pcdCircle)
    circle2 = getDistDisplay(50)
    pcdCircle2 = o3d.geometry.PointCloud()
    pcdCircle2.points = o3d.utility.Vector3dVector(circle2)
    pcdCircle2.paint_uniform_color([0.47, 0.67, 0.67])
    display.append(pcdCircle2)

    o3d.visualization.draw_geometries(display)
    
def parse_args():
    p = argparse.ArgumentParser(
        description='Model Runner')
    # p.add_argument(
    #     'binLocation', help='Path to the dir to test')
    p.add_argument(
        "-scene", help="specific scene number provide full ie 002732")
    p.add_argument(
        "-sequence", help="sequence number provide as 1 rather than 01 (default all labeled)", 
        nargs='?', const=0, default=range(0, 11))

    return p.parse_args()
    

def main():

    print("\n\n------------------------------")
    print("\n\nStarting open3D viewer\n\n")

    path = "/home/garrett/Documents/data/dataset/sequences/"

    print("Parsing {} :".format(path))

    scene = 0

    args = parse_args()

    # Get sequences

    print("Collecting Labels and Bins for sequences {}".format(args.sequence))

    binFiles = []
    labelFiles = []

    
            
    print("Starting Visualization")


    if (args.scene):
        currPath = path + str(args.sequence).rjust(2, '0')

        labelFiles = [currPath + "/labels/" + args.scene + ".label"]
        binFiles = [currPath + "/velodyne/" + args.scene + ".bin"]
    
    else:
        for sequenceNum in args.sequence:
        
            folderNum = str(sequenceNum).rjust(2, '0')
            currPath = path + folderNum

            labelFilesSeq = np.array(glob.glob(currPath + "/labels/*.label", recursive = True))
            binFilesSeq = np.array(glob.glob(currPath + "/velodyne/*.bin", recursive = True))
            print("Parsing sequence {}".format(folderNum))

            # Sort
            labelFilesSeq = sorted(labelFilesSeq)
            binFilesSeq = sorted(binFilesSeq)
            
            for labelFile in labelFilesSeq:
                labelFiles.append(labelFile)
            
            for binFile in binFilesSeq:
                binFiles.append(binFile)

    try:
        idx = random.choice(range(len(labelFiles)))
        # for idx in range(len(labelFiles)):
        print(scene, binFiles[idx])
        scene += 1
        viewOne(binFiles[idx], labelFiles[idx])
        

    except KeyboardInterrupt:
        print("\n--------------------------------------------------------")
        print("Ctrl+C pressed...")
        print("Concluding\n")



if __name__ == '__main__':
    main()




