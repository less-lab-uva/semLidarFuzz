#!/usr/bin/env python3
# This file is covered by the LICENSE file in the root of this project.

import argparse
import os
import yaml
from laserscan import LaserScan, SemLaserScan
from laserscanvis import LaserScanVis
import glob
import numpy as np


import os

if __name__ == '__main__':
  parser = argparse.ArgumentParser("./visualize.py")
  parser.add_argument(
      '--dataset', '-d',
      type=str,
      required=False,
      help='Dataset to visualize. No Default',
  )
  parser.add_argument(
      '--config', '-c',
      type=str,
      required=False,
      default="semantic-kitti.yaml",
      help='Dataset config file. Defaults to %(default)s',
  )
  parser.add_argument(
      '--sequence', '-s',
      type=str,
      default="00",
      required=False,
      help='Sequence to visualize. Defaults to %(default)s',
  )
  parser.add_argument(
      '--predictions', '-p',
      type=str,
      default=None,
      required=False,
      help='Alternate location for labels, to use predictions folder. '
      'Must point to directory containing the predictions in the proper format '
      ' (see readme)'
      'Defaults to %(default)s',
  )
  parser.add_argument(
      '--velodyne', '-v',
      type=str,
      default=None,
      required=False,
      help='Alternate location for bins, to use velodyne folder. '
      'Must point to directory containing the bins in the proper format '
      'Defaults to %(default)s',
  )
  parser.add_argument(
      '--predictionSpecific', '-ps',
      type=str,
      default=None,
      required=False,
      help='Specific Scan'
  )
  parser.add_argument(
      '--show_mongo', '-m',
      dest='show_mongo',
      default=False,
      action='store_true',
      help='Print mongo info for the mutation',
  )
  parser.add_argument(
      '--ignore_semantics', '-i',
      dest='ignore_semantics',
      default=False,
      action='store_true',
      help='Ignore semantics. Visualizes uncolored pointclouds.'
      'Defaults to %(default)s',
  )
  parser.add_argument(
      '--do_instances', '-di',
      dest='do_instances',
      default=False,
      action='store_true',
      help='Visualize instances too. Defaults to %(default)s',
  )
  parser.add_argument(
      '--offset',
      type=int,
      default=0,
      required=False,
      help='Sequence to start. Defaults to %(default)s',
  )
  parser.add_argument(
      '--ignore_safety',
      dest='ignore_safety',
      default=False,
      action='store_true',
      help='Normally you want the number of labels and ptcls to be the same,'
      ', but if you are not done inferring this is not the case, so this disables'
      ' that safety.'
      'Defaults to %(default)s',
  )
  FLAGS, unparsed = parser.parse_known_args()

  # print summary of what we will do
  print("*" * 80)
  print("INTERFACE:")
  print("Dataset", FLAGS.dataset)
  print("Config", FLAGS.config)
  print("Sequence", FLAGS.sequence)
  print("Predictions", FLAGS.predictions)
  print("ignore_semantics", FLAGS.ignore_semantics)
  print("do_instances", FLAGS.do_instances)
  print("ignore_safety", FLAGS.ignore_safety)
  print("offset", FLAGS.offset)
  print("*" * 80)

  # open config file
  try:
    print("Opening config file %s" % FLAGS.config)
    CFG = yaml.safe_load(open(FLAGS.config, 'r'))
  except Exception as e:
    print(e)
    print("Error opening yaml file.")
    quit()

  # fix sequence name
  FLAGS.sequence = '{0:02d}'.format(int(FLAGS.sequence))

  # populate the pointclouds
  scan_names = []
  if FLAGS.velodyne is not None:
    scan_names = np.array(glob.glob(FLAGS.velodyne + "/*.bin"))
  else:
    # does sequence folder exist?
    scan_paths = os.path.join(FLAGS.dataset, "sequences",
                              FLAGS.sequence, "velodyne")
    if os.path.isdir(scan_paths):
      print("Sequence folder exists! Using sequence from %s" % scan_paths)
    else:
      print("Sequence folder doesn't exist! Exiting...")
      quit()

    scan_names = [os.path.join(dp, f) for dp, dn, fn in os.walk(
        os.path.expanduser(scan_paths)) for f in fn]
  scan_names.sort()

  # LABELS
  label_names = []
  if not FLAGS.ignore_semantics:
    if FLAGS.predictionSpecific is not None:
      label_names = [FLAGS.predictionSpecific]
    elif FLAGS.predictions is not None:
      label_names = np.array(glob.glob(FLAGS.predictions + "/*.label"))
    else:
      label_paths = os.path.join(FLAGS.dataset, "sequences",
                                 FLAGS.sequence, "labels")
      if os.path.isdir(label_paths):
        print("Labels folder exists! Using labels from %s" % label_paths)
      else:
        print("Labels folder doesn't exist! Exiting...")
        quit()
      # populate the pointclouds
      label_names = [os.path.join(dp, f) for dp, dn, fn in os.walk(
          os.path.expanduser(label_paths)) for f in fn]
    
    label_names.sort()

    # Get label ids
    labelSet = set()
    for label in label_names:
      labelFileName = os.path.basename(label)
      labelString = labelFileName.replace(".label", "")
      labelSet.add(labelString)

    print("Num scans: {} Num labels {}".format(len(scan_names), len(label_names)))

    # Only use the point clouds that we have labels for
    revisedBins = []
    for scan in scan_names:
      binFileName = os.path.basename(scan)
      binString = binFileName.replace(".bin", "")
      if (binString in labelSet):
        revisedBins.append(scan)
    scan_names = revisedBins

    # check that there are same amount of labels and scans
    if not FLAGS.ignore_safety:
      print(scan_names)
      assert(len(label_names) == len(scan_names))

  # create a scan
  if FLAGS.ignore_semantics:
    scan = LaserScan(project=True)  # project all opened scans to spheric proj
  else:
    color_dict = CFG["color_map_alt"]
    nclasses = len(color_dict)
    scan = SemLaserScan(nclasses, color_dict, project=True)

  # create a visualizer
  semantics = not FLAGS.ignore_semantics
  instances = FLAGS.do_instances
  if not semantics:
    label_names = None
  vis = LaserScanVis(scan=scan,
                     scan_names=scan_names,
                     label_names=label_names,
                     offset=FLAGS.offset,
                     semantics=semantics, instances=instances and semantics,
                     mongo=FLAGS.show_mongo)

  # run the visualizer
  vis.run()
