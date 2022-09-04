"""
semFuzzLidar 
Main runner for the mutation tool

@Date 6/23/22
"""

import argparse
import os

from domain.toolSessionManager import SessionManager

import controllers.mutationTool.mutationRunner as mutationRunner
import controllers.mutationTool.redoMutation as redoMutation


# -------------------------------------------------------------
# Arguments


def parse_args():
    p = argparse.ArgumentParser(
        description='Model Runner')

    # Required params
    p.add_argument("-binPath", 
        help="Path to the sequences folder of LiDAR scan bins", 
        nargs='?', const="",
        default="")

    p.add_argument("-labelPath", 
        help="Path to the sequences label files should corrispond with velodyne", 
        nargs='?', const="",
        default="")

    p.add_argument("-predPath", 
        help="Path to the prediction label files created by the models, should corrispond with velodyne", 
        nargs='?', const="",
        default="")

    p.add_argument("-mdb", 
        help="Path to the connection string for mongo", 
        nargs='?', const="",
        default="")

    p.add_argument("-modelDir", 
        help="Path to the directory where the models are saved", 
        nargs='?', const="",
        default="")

    p.add_argument('-mutation', 
        help='mutations to perform comma seperated example: ADD_ROTATE,ADD_MIRROR_ROTATE or ADD_ROTATE defaults to ADD_ROTATE',
        nargs='?', const="ADD_ROTATE", default="ADD_ROTATE")

    p.add_argument("-batch", 
        help="Batch to create before evaluating", 
        nargs='?', const=400, default=400)

    p.add_argument("-count", 
        help="The total number of valid mutations you would like to create", 
        nargs='?', const=1, default=1)

    p.add_argument('-models', 
        help='Models (SUTs) to evaluate comma seperated: cyl,spv,sal,sq3,pol',
        nargs='?', const="cyl,spv,sal,sq3,pol", default="cyl,spv,sal,sq3,pol")


    # Tool configurable params
    p.add_argument("-saveAt", 
        help="Location to save the tool output",
        nargs='?', const=os.getcwd(), 
        default=os.getcwd())


    p.add_argument('-asyncEval', 
        help='Seperates the evaluation into its own process to run asyncronusly to the mutation generation',
        action='store_true', default=False)


    # Optional Flags
    p.add_argument('-vis', 
        help='Visualize with Open3D',
        action='store_true', default=False)

    p.add_argument('-ne', help='Disables Evaluation',
        action='store_false', default=True)

    p.add_argument('-ns', help='Disables Saving',
        action='store_false', default=True)

    p.add_argument('-saveAll', help='Disables Deletion',
        action='store_true', default=False)

    p.add_argument('-saveNum', help='Count to save from the top loss',
                   nargs='?', const=10, default=10)
    p.add_argument('-threadCount', help='Number of threads to use for generating mutations',
                   nargs='?', const=1, default=1)

    p.add_argument('-removeRandom', help='REMOVE will try to select randomly instead of iterating through assets',
        action='store_true', default=False)
        

    # Debug options to set asset / scene
    p.add_argument("-assetId", 
        help="Asset Identifier, optional forces the tool to choose one specific asset", 
        nargs='?', const=None, default=None)
    p.add_argument("-sequence", 
        help="Sequences number, provide as 00 CANNOT BE USED WITHOUT scene backdoor to force add to choose base scene", 
        nargs='?', const=None, default=None)
    p.add_argument( "-scene", 
        help="Specific scene number provide full ie 002732, CANNOT BE USED WITHOUT sequence",
        nargs='?', const=None, default=None)
    

    # Mutation debug / recreation options
    # Rotate
    p.add_argument('-rotate', 
        help='Value to rotate', 
        default=None,
        required=False)
    # Mirror
    p.add_argument('-mirror', 
        help='Value to mirror', 
        default=None,
        required=False)
    # Intensity
    p.add_argument('-intensity', 
        help='Value to change intensity', 
        default=None,
        required=False)
    # Scale
    p.add_argument('-scale', 
        help='Value to scale by', 
        default=None,
        required=False)
    # Sign
    p.add_argument('-sign', 
        help='Sign to replace with', 
        default=None,
        required=False)
    # Deform
    p.add_argument('-deformPercent', 
        help='Amount of the asset to deform', 
        default=None,
        required=False)
    p.add_argument('-deformPoint', 
        help='Point to deform from', 
        default=None,
        required=False)
    p.add_argument('-deformMu', 
        help='Mean for random deformation', 
        default=None,
        required=False)
    p.add_argument('-deformSigma', 
        help='Sigma for random deformation', 
        default=None,
        required=False)
    p.add_argument('-deformSeed', 
        help='Sigma for random deformation', 
        default=None,
        required=False)


    # Redo options
    p.add_argument('-redoBatchId', 
        help='Recreate a batch',
        nargs='?', const=None, default=None)
    p.add_argument('-redoMutationId', 
        help='Recreate a mutation',
        nargs='?', const=None, default=None)
    
    
    return p.parse_args()

    


# ----------------------------------------------------------

def main():

    print("\n\n------------------------------")
    print("\n\nStarting Semantic LiDAR Fuzzer\n\n")
    
    # Get arguments 
    args = parse_args()
    
    # Perform the setup creating a session manager
    sessionManager = SessionManager(args)

    # Either recreate a mutation, rerun and entire batch, OR run the tool
    if (sessionManager.redoBatchId != None):
        redoMutation.batchRecreation(sessionManager.redoBatchId, sessionManager)
    elif (sessionManager.redoMutationId != None):
        redoMutation.mutationRecreation(sessionManager.redoMutationId, sessionManager)
    else:
        mutationRunner.runMutations(sessionManager)



if __name__ == '__main__':
    main()



