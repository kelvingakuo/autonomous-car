import glob
import os

from subprocess import call

offending = "D:/===/== BIG-ASS DATASETS/FINAL/_____________ LABEL THESE/remove_these"

offending1 = "D:/===/== BIG-ASS DATASETS/FINAL/_____________ LABEL THESE/Camera"
offending2 = "D:/===/== BIG-ASS DATASETS/FINAL/_____________ LABEL THESE/Scene"

toClean = "D:/CODE/DATA/car_updated/AUTONOMOUS-SELF-DRVING-CAR/project_restructured/computer/models/training_data/Complete_Detection_Dataset_v3/dump"
whereTo = "D:/CODE/DATA/car_updated/AUTONOMOUS-SELF-DRVING-CAR/project_restructured/computer/models/training_data/Complete_Detection_Dataset_v4/dump"


# jpgs1 = [os.path.basename(x) for x in glob.glob(offending1 + "/*.jpg")]
# jpg2 = [os.path.basename(x) for x in glob.glob(offending2 + "/*.jpg")]
# jpgs = jpgs1 + jpg2
# xmls1 = [os.path.basename(x) for x in glob.glob(offending1 + "/*.xml")]
# xmls2 = [os.path.basename(x) for x in glob.glob(offending2 + "/*.xml")]
# xmls = xmls1 + xmls2


jpgs = [os.path.basename(x) for x in glob.glob(offending + "/*.jpg")]
xmls = [os.path.basename(x) for x in glob.glob(offending + "/*.xml")]

toCleanJPGs = [os.path.basename(x) for x in glob.glob(toClean + "/*.jpg")]
toCleanXMLs = [os.path.basename(x) for x in glob.glob(toClean + "/*.xml")]


newJPGs = [jpg for jpg in toCleanJPGs if jpg not in jpgs]
newXMLs = [xml for xml in toCleanXMLs if xml not in xmls]

print(len(toCleanJPGs))
print(len(newJPGs))
print(len(toCleanXMLs))
print(len(newXMLs))

for jpg in newJPGs:
	src = toClean + "/" + jpg
	dest = whereTo

	print(src)
	print(dest)
	call("cp " + src + " " + dest, shell = True)
	print("=============================")


for xml in newXMLs:
	src = toClean + "/" + xml
	dest = whereTo

	print(src)
	print(dest)
	call("cp " + src + " " + dest, shell = True)
	print("=============================")
