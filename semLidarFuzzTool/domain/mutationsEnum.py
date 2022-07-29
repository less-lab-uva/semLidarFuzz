"""
Enums for the different mutations made up of 
asset location
and transformation
"""

from enum import Enum


# ----------------------------------------------------------
# Where the asset will come from 
# (ADD, any scene or SCENE the specific scene)
# What type of asset will be utilized 
# Currenly have SIGN and VEHICLE type specific mutations


class AssetLocation(Enum):
    ADD = "ADD"
    SCENE = "SCENE"
    SIGN = "SIGN" # subset of scene
    VEHICLE = "VEHICLE" # subset of scene


# ----------------------------------------------------------
# What transformations will be performed on that asset
# Three main classifications of transformations
# ADD, REMOVE, and CHANGE


class Transformation(Enum):
    # ADD
    ROTATE = "ROTATE" # ADD
    MIRROR = "MIRROR"  # ADD
    # REMOVE
    REMOVE = "REMOVE" # SCENE
    # CHANGE
    REPLACE = "REPLACE" # SIGN
    INTENSITY = "INTENSITY" # Vehicle
    DEFORM = "DEFORM" # Vehicle
    SCALE = "SCALE" # Vehicle


# ----------------------------------------------------------
# Enum of the different types of mutations supported


class Mutation(Enum):
    ADD_ROTATE = AssetLocation.ADD.name + "_" + Transformation.ROTATE.name,
    ADD_MIRROR_ROTATE = AssetLocation.ADD.name + "_" + Transformation.MIRROR.name + "_" + Transformation.ROTATE.name,
    SCENE_REMOVE = AssetLocation.SCENE.name + "_" + Transformation.REMOVE.name,
    SIGN_REPLACE = AssetLocation.SIGN.name + "_" + Transformation.REPLACE.name,
    VEHICLE_INTENSITY = AssetLocation.VEHICLE.name + "_" + Transformation.INTENSITY.name,
    VEHICLE_DEFORM = AssetLocation.VEHICLE.name + "_" + Transformation.DEFORM.name,
    VEHICLE_SCALE = AssetLocation.VEHICLE.name + "_" + Transformation.SCALE.name,




