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

## Resources Collected from SemanticKITTI
|Type Name|Total Count|Selected Count|%|
|---|---|---|---|
|car|205784|44893|21.8% |
|traffic-sign|0|8443|-|
|moving-car|8933|3503|39.2% |
|moving-person|5895|1534|26.0% |
|moving-bicyclist|2874|1368|47.6% |
|other-vehicle|10478|888|8.5% |
|motorcycle|4586|749|16.3% |
|person|6339|486|7.7% |
|moving-motorcyclist|555|473|85.2% |
|truck|2643|421|15.9% |
|bicycle|10602|449|4.2% |
|moving-bus|79|45|57.0% |
|moving-other-vehicle|220|36|16.4% |
|motorcyclist|171|20|11.7% |
|moving-truck|172|15|8.7% |
|bicyclist|6|0|0.0% |
|bus|10|0|0.0% |
|**Total**|**259347**|**63323**|**24.4%**|




