# Extract Instances

Scripts to perform setup task of preloading asset data

---

## Instance extractor

- assetValidDemoV4.py
- Obtains the valid instances to use in mutation
- Loads the mongo with the assets
- Creates a new set of label files with instances that match the mongo assets

### Arguments
| Argument | Usage |
| ----- | ------------ |
| ```-binPath PATH``` | Path to the scan bin files, expected to be given in the format of /path/dataset/sequences |
| ```-mdb PATH``` | Path to the mongoconnect.txt file with the connection url string |
| ```-saveAt PATH``` | Path to the location to save the label files |

---

## Asset Valid Demo

- assetValidDemoV4.py
- Visualizes the selection process for the instance extractor 

---



