# Use CSV of the full dataset to split the dataset into train and test

import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from subprocess import call

df = pd.read_csv("v5_complete_dataset.csv")

dfTrain, dfTest = train_test_split(df, test_size=0.1)


print(df.shape)

print(dfTrain.shape)
print(dfTest.shape)


testFolder = "D:/CODE/DATA/car_updated/AUTONOMOUS-SELF-DRVING-CAR/project_restructured/computer/models/training_data/Complete_Detection_Dataset_v5/test/"
trainFolder = "D:/CODE/DATA/car_updated/AUTONOMOUS-SELF-DRVING-CAR/project_restructured/computer/models/training_data/Complete_Detection_Dataset_v5/train/"

origiFolder = "D:/CODE/DATA/car_updated/AUTONOMOUS-SELF-DRVING-CAR/project_restructured/computer/models/training_data/Complete_Detection_Dataset_v5/dump/"


for index, row in dfTrain.iterrows():
	img = row["filename"]
	xml = row["filename"][:-3] + "xml"


	sourceImg = origiFolder + img
	destImg = trainFolder

	sourceAnnot = origiFolder + xml
	destAnnot = trainFolder


	call("cp " + sourceImg + " " + destImg, shell = True)
	call("cp " + sourceAnnot + " " + destAnnot, shell = True)



	print(sourceImg)
	print(destImg)

	print(sourceAnnot)
	print(destAnnot)

	print("============================================================")



for index, row in dfTest.iterrows():
	img = row["filename"]
	xml = row["filename"][:-3] + "xml"


	sourceImg = origiFolder + img
	destImg = testFolder

	sourceAnnot = origiFolder + xml
	destAnnot = testFolder


	call("cp " + sourceImg + " " + destImg, shell = True)
	call("cp " + sourceAnnot + " " + destAnnot, shell = True)



	print(sourceImg)
	print(destImg)

	print(sourceAnnot)
	print(destAnnot)

	print("============================================================")












