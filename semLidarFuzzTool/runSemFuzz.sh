#!/bin/bash



# -------------------------------------------------------------------------------------------------------------------

# Options

# mut="ADD_ROTATE"
# mut="ADD_MIRROR_ROTATE"
mut="SCENE_REMOVE"
# mut="SIGN_REPLACE"
# mut="VEHICLE_DEFORM"
# mut="VEHICLE_INTENSITY"
# mut="VEHICLE_SCALE"

binPath="/home/garrett/Documents/data/dataset/sequences/"
lblPath="/home/garrett/Documents/data/dataset4/sequences/"
predPath="/home/garrett/Documents/data/resultsBase/"
# saveTo="/media/garrett/ExtraDrive1"

seq="00"
scene="000000"
# seq="04"
# scene="000244"
seq="08"
scene="000701"
# assetId="00-000000-213"
assetId="00-002452-132-car"
assetId="00-002452-129-car"
assetId="00-000450-282-car"
assetId="00-004159-431-car"
# assetId="01-000050-1389-traffic-sign"
# assetId="01-000050-1389-traffic-sign"
# assetId="02-000065-1837-traffic-sign"
# assetId="00-000014-1-moving-motorcyclist"
# assetId="08-003459-1023-traffic-sign"
# assetId="00-000003-213-car"
# assetId="00-000000-1"
# assetId="00-000156-6"
# assetId="04-000050-6-moving-car"
# assetId="08-000368-12-other-vehicle"
# assetId="06-000882-3-truck"
count=1
batch=40
models="cyl,spv,sal,sq3,pol"


# -------------------------------------------------------------------------------------------------------------------

# Run command 
cd controllers/mutationTool
python semFuzzLidar.py -binPath "$binPath" -labelPath $lblPath -predPath $predPath -m $mut -count $count -b $batch -ns -vis

# python semFuzzLidar.py -path "$velPath" -lbls $lblPath
# python semFuzzLidar.py -binPath "$binPath" -labelPath $lblPath -predPath $predPath -m $mut -count $count -b $batch -ns -assetId $assetId -vis 
# python semFuzzLidar.py -binPath "$binPath" -labelPath $lblPath -predPath $predPath -m $mut -count $count -b $batch
# python semFuzzLidar.py -binPath "$binPath" -labelPath $lblPath -predPath $predPath -m $mut -count $count -b $batch -saveAt $saveTo
# python semFuzzLidar.py -binPath "$binPath" -labelPath $lblPath -m $mut -count $count -b $batch -asyncEval
# python semFuzzLidar.py -binPath "$binPath" -labelPath $lblPath -m $mut -count $count -b $batch -assetId $assetId -vis
# python semFuzzLidar.py -binPath "$binPath" -labelPath $lblPath -m $mut -count $count -b $batch
# python semFuzzLidar.py -binPath "$binPath" -labelPath $lblPath -m $mut -count $count -b $batch -asyncEval
# python semFuzzLidar.py -binPath "$binPath" -labelPath $lblPath -m $mut -count $count -b $batch -assetId $assetId -ns -vis
# python semFuzzLidar.py -path "$basePath" -m $mut -vis -ns
# python semFuzzLidar.py -path "$basePath" -m $mut -seq $seq -scene $scene -ns -vis
# python semFuzzLidar.py -path "$basePath" -m $mut -seq $seq -scene $scene -ns
# python semFuzzLidar.py -path "$basePath" -m $mut -seq $seq -scene $scene -vis -assetId $assetId -rotate 323
# python semFuzzLidar.py -path "$velPath" -lbls $lblPath -m $mut -count $count -b $batch -assetId $assetId -rotate 116 -seq $seq -scene $scene

# -------------------------------------------------------------------------------------------------------------------




