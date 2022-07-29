#!/bin/bash


# ------------------------------------------------------------------------------------------------


# SET DIRS
# ./visualizeCustom.py -m -p /home/garrett/Documents/lidarTest2/toolV2/data/done/labels/cyl -v /home/garrett/Documents/lidarTest2/toolV2/data/done/velodyne
# ./visualizeCustom.py -p /home/garrett/Documents/lidarTest2/toolV2/data/done/labels/cyl -v /home/garrett/Documents/lidarTest2/toolV2/data/done/velodyne
# ./visualizeCustom.py -m -p /home/garrett/Documents/lidarTest2/toolV2/data/done/labels/cyl -v /home/garrett/Documents/lidarTest2/toolV2/data/done/velodyne

# lbls="/home/garrett/Documents/lidarTest2/toolV3/data/done/labels/cyl"
# vels="/home/garrett/Documents/lidarTest2/toolV3/data/done/velodyne"
# ./visualizeCustom.py -m -p $lbls -v $vels



# ------------------------------------------------------------------------------------------------

# SPECIFIC SCAN

# scan=/home/garrett/Documents/lidarTest2/toolV2/data/done/labels/actual/SWkv7xQDJc7Q845X7uiTFc-ADD_ROTATE.label
# scan=/home/garrett/Documents/lidarTest2/toolV2/data/done/labels/spv/ZEc4TVVh3Med3725tTA6mT-ADD_ROTATE.label

# scan="/home/garrett/Documents/data/dataset/sequences/05/labels/001139.label" 
# vel="/home/garrett/Documents/data/dataset/sequences/05/velodyne"
# scan="/home/garrett/Documents/lidarTest2/toolV5/finalVisualize/finalvis/SIGN_REPLACE/data/done/labels/cyl/5dn3DRKAYZSAqyFGLJUvRw-SIGN_REPLACE.label" 
# vel="/home/garrett/Documents/lidarTest2/toolV5/finalVisualize/finalvis/SIGN_REPLACE/data/done/velodyne"
# scan=/home/garrett/Documents/lidarTest2/toolV5/data/done/labels/actual/jK42Fj2adSqwkfg4U6ZtBi-SCENE_REMOVE.label
# vel=/home/garrett/Documents/lidarTest2/toolV5/data/done/velodyne
# scan=/home/garrett/Documents/lidarTest2/toolV5/data/done/labels/actual/L5VUgaVwkG7U2moAuVhiAF-ADD_ROTATE.label
# vel=/home/garrett/Documents/lidarTest2/toolV5/data/done/velodyne
scan=/home/garrett/Documents/data/out/sequences/00/predictions/000000.label
# scan=/home/garrett/Documents/data/out/000000.label
vel="/home/garrett/Documents/data/dataset/sequences/00/velodyne"
# scan=/home/garrett/Documents/data/resultsBase/00/pol/000000.label


./visualizeCustom.py -ps $scan -v $vel

# ./visualizeCustom.py -ps 


# ------------------------------------------------------------------------------------------------










