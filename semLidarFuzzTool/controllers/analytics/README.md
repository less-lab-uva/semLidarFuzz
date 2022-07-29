# Analytics

Scripts to perform analysis on the collected details and final data

---

## Duplicate Checker

- duplicateChecker.py
- Can be run to do duplicate analysis on a given batch
- Note this functionality was baked into the final details, so this is just if you'd like to change the duplicate definition

---

## Points Changed vs Accuracy 

- pointsAccCsv.py
- Script that produces a csv comparing the points changed and the accuracy obtained

---

## Produce CSV

- produceCsv.py
- Script that converts a final data JSON into an accuracy csv and jaccard csv
- Easier to visualize this data than in the JSON format

### Arguments
| Argument | Usage |
| ----- | ------------ |
| ```-data PATH``` | Path to the directory where the tool's output directory is stored (Either data or id must be provided) |
| ```-id ID``` | Optional parameter to fetch the final data by id from mongo rather than pulling the data from the tool output directory (Eithr data or id must be provided) |
| ```-mdb PATH``` | Path to the mongoconnect.txt file with the connection url string |
| ```-saveAt PATH``` | Path to the location to save the csv output |


---

## Recreate Final Data

- recreateFinalData.py
- Script that will recreate a final data JSON for a given run
- Could be helpful if you'd like to change the bucket definitions without rerunning the tool

---



