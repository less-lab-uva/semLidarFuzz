# Final Visualize

Script to visualize the data after a run

---

## Final Visualization

- finalVisualization.py
- Converts the output of the tool into range image comparisions 
- Adapted from https://github.com/PRBonn/semantic-kitti-api/blob/master/visualize.py



### Arguments
| Argument | Usage |
| ----- | ------------ |
| ```-binPath PATH``` | Path to the scan bin files, expected to be given in the format of /path/dataset/sequences |
| ```-labelPath PATH``` | Path to the label files, expected to be given in the format of /path/dataset/sequences |
| ```-predPath PATH``` | Path to the models original prediction files, expect that following the directory given are the model directories each with the seq and scenes predictions |
| ```-toolOutputPath PATH``` | Path to the directory where the tool's output is stored (path should end with output) |
| ```-mdb PATH``` | Path to the mongoconnect.txt file with the connection url string |
| ```-saveAt PATH``` | Path to the location to save the final visualization png images |

---




