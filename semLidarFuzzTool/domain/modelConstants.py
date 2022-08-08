"""
Constants for models
Including enum of model abreviations
Model directory names
"""

from enum import Enum


# ----------------------------------------------------------
# Model Abreviation Enum


class Models(Enum):
    CYL = "cyl"
    SPV = "spv"
    SAL = "sal"
    SQ3 = "sq3"
    POL = "pol"
    RAN = "ran"
    JS3CCPU = "js3c_cpu"
    JS3CGPU = "js3c_gpu"


# ----------------------------------------------------------
# Model directory names


CYL_DIRECTORY_NAME = "Cylinder3D"
SPV_DIRECTORY_NAME = "spvnas"
SAL_DIRECTORY_NAME = "SalsaNext"
SQ3_DIRECTORY_NAME = "SqueezeSegV3"
POL_DIRECTORY_NAME = "PolarSeg"
RAN_DIRECTORY_NAME = "RandLA-Net"
JS3CCPU_DIRECTORY_NAME = "JS3C-Net"
JS3CGPU_DIRECTORY_NAME = "JS3C-Net"


# ----------------------------------------------------------


