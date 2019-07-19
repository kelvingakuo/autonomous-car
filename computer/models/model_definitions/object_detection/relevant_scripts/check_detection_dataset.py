# Check 1:1 relationship for XMLs and pics in dataset v1 
import glob
import re
import os


full = "../../training_data/Complete_Detection_Dataset_v5/dump"


xmls = glob.glob(full + "/*.xml")
pngs = glob.glob(full + "/*.png")
jpgs = glob.glob(full + "/*.jpg")



actualXMLS = [os.path.basename(xml) for xml in xmls]
actualJpgs = [os.path.basename(jpg) for jpg in jpgs]
actualPngs = [os.path.basename(png) for png in pngs]

xmlNames = [re.search(r"(.*).xml", xmlFil, re.I|re.M).group(1) for xmlFil in actualXMLS]
jpgNames = [re.search(r"(.*).jpg", jpg, re.I|re.M).group(1) for jpg in actualJpgs]
pngNames = [re.search(r"(.*).png", png, re.I|re.M).group(1) for png in actualPngs]
picNames = jpgNames + pngNames

print(len(xmlNames))
print(len(picNames))

print(set(xmlNames) - set(picNames)) # Should be an empty set