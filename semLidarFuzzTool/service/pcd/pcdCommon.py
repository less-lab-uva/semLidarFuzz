"""
pcdUtil
Functions for performing the mutations and manipulating the point clouds

@Date 6/23/22
"""


import numpy as np
import open3d as o3d
import math
import sys


# --------------------------------------------------------------------------
# Constants


centerCamPoint = np.array([0, 0, 0.3])


# --------------------------------------------------------------------------
# Util


"""
removeAssetScene

Removes a given asset from a scene 
Returns the scene with out the points that overlapped with the asset
"""
def removeAssetScene(pcdArrAsset, pcdArr, intensity, semantics, instances):
    mask = np.ones(np.shape(pcdArr)[0], dtype=bool)

    pointsSet = set()

    for point in pcdArrAsset:
        pointsSet.add((point[0], point[1], point[2]))

    for index in range(0, np.shape(pcdArr)[0]):
        if ((pcdArr[index][0], pcdArr[index][1], pcdArr[index][2]) in pointsSet):
            mask[index] = False

    pcdArrRemoved = pcdArr[mask]
    intensityRemoved = intensity[mask]
    semanticsRemoved = semantics[mask]
    instancesRemoved = instances[mask]

    return pcdArrRemoved, intensityRemoved, semanticsRemoved, instancesRemoved, mask


"""
combine

Combines the points, intensity, semantics, instances
For two seperate sets of points
"""
def combine(pcdArr, intensity, semantics, instances, pcdArrAsset, intensityAsset, semanticsAsset, instancesAsset):
    pcdArrCombined = np.vstack((pcdArr, pcdArrAsset))
    intensityCombined = np.hstack((intensity, intensityAsset))
    semanticsCombined = np.hstack((semantics, semanticsAsset))
    instancesCombined = np.hstack((instances, instancesAsset))

    return pcdArrCombined, intensityCombined, semanticsCombined, instancesCombined


# --------------------------------------------------------------------------
# Rotate


"""
rotatePoints

Rotates points by a given angle around the center camera
"""
def rotatePoints(points, angle):
    # Preconditions for asset rotation
    if (angle < 0 or angle > 360):
        print("Only angles between 0 and 360 are accepable")
        exit()
    elif (not np.size(points)):
        print("Points are empty")
        exit()

    # Do nothing if asked to rotate to the same place
    if (angle == 0 or angle == 360):
        return points

    pointsRotated = np.copy(points)
    for point in pointsRotated:
        pt = (point[0], point[1])
        newLocation = rotateOnePoint((0, 0), pt, angle)
        point[0] = newLocation[0]
        point[1] = newLocation[1]

    return pointsRotated


"""
rotateOnePoint

Rotate a point counterclockwise by a given angle around a given origin.
In degrees
"""
def rotateOnePoint(origin, point, angle):

    radians = (angle * math.pi) / 180
    return rotateOnePointRadians(origin, point, radians)


"""
rotateOnePointRadians

Rotate a point counterclockwise by a given angle around a given origin.
In radians
https://stackoverflow.com/questions/34372480/rotate-point-about-another-point-in-degrees-python
"""
def rotateOnePointRadians(origin, point, radians):

    ox, oy = origin
    px, py = point

    qx = ox + math.cos(radians) * (px - ox) - math.sin(radians) * (py - oy)
    qy = oy + math.sin(radians) * (px - ox) + math.cos(radians) * (py - oy)
    return qx, qy


"""
getAngleRadians

gets the angle in radians created between p0 -> p1 and p0 -> p2
p0 is the origin

https://stackoverflow.com/questions/1211212/how-to-calculate-an-angle-from-three-points
"""
def getAngleRadians(p0, p1, p2):
    p0x = p0[0] 
    p0y = p0[1]
    p1x = p1[0] 
    p1y = p1[1]
    p2x = p2[0]
    p2y = p2[1]

    p01 = math.sqrt(((p0x - p1x) * (p0x - p1x)) + ((p0y - p1y) * (p0y - p1y)))
    p02 = math.sqrt(((p0x - p2x) * (p0x - p2x)) + ((p0y - p2y) * (p0y - p2y)))
    p12 = math.sqrt(((p1x - p2x) * (p1x - p2x)) + ((p1y - p2y) * (p1y - p2y)))

    result = np.arccos(((p01 * p01) + (p02 * p02) - (p12 * p12)) / (2 * p01 * p02))

    return result


# --------------------------------------------------------------------------
# Mesh & Shadow


"""
checkInclusionBasedOnTriangleMesh

Creates a mask the size of the points array
True is included in the mesh
False is not included in the mesh
"""
def checkInclusionBasedOnTriangleMesh(points, mesh):

    obb = mesh.get_oriented_bounding_box()

    legacyMesh = o3d.t.geometry.TriangleMesh.from_legacy(mesh)

    mask = np.zeros((np.shape(points)[0],), dtype=bool)

    scene = o3d.t.geometry.RaycastingScene()
    _ = scene.add_triangles(legacyMesh)

    # pcdAsset = o3d.geometry.PointCloud()
    pointsVector = o3d.utility.Vector3dVector(points)

    indexesWithinBox = obb.get_point_indices_within_bounding_box(pointsVector)

    for idx in indexesWithinBox:
        pt = points[idx]
        query_point = o3d.core.Tensor([pt], dtype=o3d.core.Dtype.Float32)

        occupancy = scene.compute_occupancy(query_point)
        mask[idx] = (occupancy == 1)

    return mask


"""
getLidarShadowMesh

https://math.stackexchange.com/questions/83404/finding-a-point-along-a-line-in-three-dimensions-given-two-points
"""
def getLidarShadowMesh(asset):

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

    # hull2.scale(0.5, hull2.get_center())
    hull2Vertices = np.asarray(hull2.vertices)

    combinedVertices = np.vstack((hullVertices, hull2Vertices))

    pcdShadow = o3d.geometry.PointCloud()
    pcdShadow.points = o3d.utility.Vector3dVector(combinedVertices)
    shadowMesh, _ = pcdShadow.compute_convex_hull()

    return shadowMesh


# --------------------------------------------------------------------------
# Left & Right


"""
getLeftAndRightEdges

Get the left and right points of the hull
Gets the perpendicular distance to center line taking max of each side 
NOTE Left is synonymous for counter clockwise
"""
def getLeftAndRightEdges(hull):
    
    hullVertices = np.asarray(hull.vertices)
    midPoint = hull.get_center()
    leftMax = sys.maxsize * -1
    rightMax = sys.maxsize * -1
    leftPoint = [0, 0, 0]
    rightPoint = [0, 0, 0]
    for point in hullVertices:
        distFromCenterLine = perpDistToLine(centerCamPoint, midPoint, point)

        if (isLeft(midPoint, centerCamPoint, point)):
            if (distFromCenterLine > leftMax):
                leftMax = distFromCenterLine
                leftPoint = point
        else:
            if (distFromCenterLine > rightMax):
                rightMax = distFromCenterLine
                rightPoint = point


    return leftPoint, rightPoint


"""
perpDistToLine
Gets the perpendicular distance from a point to the line between two points

https://math.stackexchange.com/questions/422602/convert-two-points-to-line-eq-ax-by-c-0
https://www.geeksforgeeks.org/perpendicular-distance-between-a-point-and-a-line-in-2-d/
"""
def perpDistToLine(lineP1, lineP2, point):
    x1 = lineP1[0]
    y1 = lineP1[1]
    x2 = lineP2[0]
    y2 = lineP2[1]
    x3 = point[0]
    y3 = point[1]

    a = y1 - y2
    b = x2 - x1
    c = (x1 * y2) - (x2 * y1)

    dist = abs((a * x3 + b * y3 + c)) / (math.sqrt(a * a + b * b))

    return dist


"""
isLeft

Checks if point (c) is left of the line drawn from a to b
Left is the same as counter clockwise given a is the camera

https://stackoverflow.com/questions/1560492/how-to-tell-whether-a-point-is-to-the-right-or-left-side-of-a-line
a = line point 1; b = line point 2; c = point to check against.
"""
def isLeft(lineP1, lineP2, point):
    aX = lineP1[0]
    aY = lineP1[1]
    bX = lineP2[0]    
    bY = lineP2[1]
    cX = point[0]
    cY = point[1]
    return ((bX - aX) * (cY - aY) - (bY - aY) * (cX - aX)) > 0





