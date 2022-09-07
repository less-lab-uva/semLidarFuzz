"""
semanticMapping 
Contains the dictionaries for mapping SemanticKITTI's semantic classes

Drawn from
https://github.com/PRBonn/semantic-kitti-api/blob/master/config/semantic-kitti.yaml
"""


# -------------------------------------------------------


name_label_mapping = {
    0: 'unlabeled',
    1: 'outlier',
    10: 'car',
    11: 'bicycle',
    13: 'bus',
    15: 'motorcycle',
    16: 'on-rails',
    18: 'truck',
    20: 'other-vehicle',
    30: 'person',
    31: 'bicyclist',
    32: 'motorcyclist',
    40: 'road',
    44: 'parking',
    48: 'sidewalk',
    49: 'other-ground',
    50: 'building',
    51: 'fence',
    52: 'other-structure',
    60: 'lane-marking',
    70: 'vegetation',
    71: 'trunk',
    72: 'terrain',
    80: 'pole',
    81: 'traffic-sign',
    99: 'other-object',
    252: 'moving-car',
    253: 'moving-bicyclist',
    254: 'moving-person',
    255: 'moving-motorcyclist',
    256: 'moving-on-rails',
    257: 'moving-bus',
    258: 'moving-truck',
    259: 'moving-other-vehicle'
}

instances = {
    10: 'car',
    11: 'bicycle',
    13: 'bus',
    15: 'motorcycle',
    18: 'truck',
    20: 'other-vehicle',
    30: 'person',
    31: 'bicyclist',
    32: 'motorcyclist',
    252: 'moving-car',
    253: 'moving-bicyclist',
    254: 'moving-person',
    255: 'moving-motorcyclist',
    257: 'moving-bus',
    258: 'moving-truck',
    259: 'moving-other-vehicle'
}

instancesVehicle = {
    10: 'car',
    11: 'bicycle',
    13: 'bus',
    15: 'motorcycle',
    18: 'truck',
    20: 'other-vehicle',
    # 31: 'bicyclist',
    # 32: 'motorcyclist',
    252: 'moving-car',
    # 253: 'moving-bicyclist',
    # 255: 'moving-motorcyclist',
    257: 'moving-bus',
    258: 'moving-truck',
    259: 'moving-other-vehicle'
}


instancesWalls = {
    50: 'building',
    51: 'fence',
    52: 'other-structure',
    71: 'trunk',
    80: 'pole',
    81: 'traffic-sign',
    99: 'other-object',
}


color_map_alt_rgb = { # rgb
    # 0 : [0, 0, 0], # Note this is changed to visually differentiate unlabeled vs outlier
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


color_map_alt_bgr = { # bgr
#   0 : [0, 0, 0], # Note this is changed to visually differentiate unlabeled vs outlier
  0 : [220, 220, 220],
  1 : [0, 0, 0],
  10: [245, 150, 100],
  11: [245, 230, 100],
  13: [250, 0, 0],
  15: [150, 60, 30],
  16: [255, 0, 0],
  18: [180, 30, 80],
  20: [255, 0, 0],
  30: [30, 30, 255],
  31: [200, 40, 255],
  32: [90, 30, 150],
  40: [255, 0, 255],
  44: [255, 150, 255],
  48: [75, 0, 75],
  49: [75, 0, 175],
  50: [0, 200, 255],
  51: [50, 120, 255],
  52: [0, 0, 0],
  60: [255, 0, 255],
  70: [0, 175, 0],
  71: [0, 60, 135],
  72: [80, 240, 150],
  80: [150, 240, 255],
  81: [0, 0, 255],
  99: [0, 0, 0],
  252: [245, 150, 100],
  253: [200, 40, 255],
  254: [30, 30, 255],
  255: [90, 30, 150],
  256: [255, 0, 0],
  257: [250, 0, 0],
  258: [180, 30, 80],
  259: [255, 0, 0],
}


learning_map = {
    0 : 0,     # "unlabeled"
    1 : 0,     # "outlier" mapped to "unlabeled" --------------------------mapped
    10: 1,     # "car"
    11: 2,     # "bicycle"
    13: 5,     # "bus" mapped to "other-vehicle" --------------------------mapped
    15: 3,     # "motorcycle"
    16: 5,     # "on-rails" mapped to "other-vehicle" ---------------------mapped
    18: 4,     # "truck"
    20: 5,     # "other-vehicle"
    30: 6,     # "person"
    31: 7,     # "bicyclist"
    32: 8,     # "motorcyclist"
    40: 9,     # "road"
    44: 10,    # "parking"
    48: 11,    # "sidewalk"
    49: 12,    # "other-ground"
    50: 13,    # "building"
    51: 14,    # "fence"
    52: 0,    # "other-structure" mapped to "unlabeled" ------------------mapped
    60: 9,     # "lane-marking" to "road" ---------------------------------mapped
    70: 15,    # "vegetation"
    71: 16,    # "trunk"
    72: 17,    # "terrain"
    80: 18,    # "pole"
    81: 19,    # "traffic-sign"
    99: 0,    # "other-object" to "unlabeled" ----------------------------mapped
    252: 1,    # "moving-car" to "car" ------------------------------------mapped
    253: 7,    # "moving-bicyclist" to "bicyclist" ------------------------mapped
    254: 6,    # "moving-person" to "person" ------------------------------mapped
    255: 8,    # "moving-motorcyclist" to "motorcyclist" ------------------mapped
    256: 5,    # "moving-on-rails" mapped to "other-vehicle" --------------mapped
    257: 5,    # "moving-bus" mapped to "other-vehicle" -------------------mapped
    258: 4,    # "moving-truck" to "truck" --------------------------------mapped
    259: 5,    # "moving-other"-vehicle to "other-vehicle" ----------------mapped
}

learning_map_inv = { # inverse of previous map
    0: 0,      # "unlabeled", and others ignored
    1: 10,     # "car"
    2: 11,     # "bicycle"
    3: 15,     # "motorcycle"
    4: 18,     # "truck"
    5: 20,     # "other-vehicle"
    6: 30,     # "person"
    7: 31,     # "bicyclist"
    8: 32,     # "motorcyclist"
    9: 40,     # "road"
    10: 44,    # "parking"
    11: 48,    # "sidewalk"
    12: 49,    # "other-ground"
    13: 50,    # "building"
    14: 51,    # "fence"
    15: 70,    # "vegetation"
    16: 71,    # "trunk"
    17: 72,    # "terrain"
    18: 80,    # "pole"
    19: 81,    # "traffic-sign"
}

learning_ignore = { # Ignore classes
    0: True,      # "unlabeled", and others ignored
    1: False,     # "car"
    2: False,     # "bicycle"
    3: False,     # "motorcycle"
    4: False,     # "truck"
    5: False,     # "other-vehicle"
    6: False,     # "person"
    7: False,     # "bicyclist"
    8: False,     # "motorcyclist"
    9: False,     # "road"
    10: False,    # "parking"
    11: False,    # "sidewalk"
    12: False,    # "other-ground"
    13: False,    # "building"
    14: False,    # "fence"
    15: False,    # "vegetation"
    16: False,    # "trunk"
    17: False,    # "terrain"
    18: False,    # "pole"
    19: False    # "traffic-sign"
}




