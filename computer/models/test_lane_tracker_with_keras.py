from keras.models import load_model
import cv2
import glob
import numpy as np
import math
import re
import time
import pandas as pd
import matplotlib.pyplot as plt


dataImgs = glob.glob("test_data_for_lane_tracker/*.jpg")
model = load_model("model_definitions/lane_tracker/checkpoint.h5")

truths = []
preds = []

for imgName in dataImgs[0:50]:
	img = cv2.imread(imgName)
	img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
	h, w, c = img.shape
	xh = int(0.25 * h)
	img = img[xh: ,: ,:] # Crop top half
	img = cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
	img = cv2.GaussianBlur(img, (3, 3,), 0)
	processedImg = cv2.resize(img, (200, 66))
	processedImg = np.expand_dims(processedImg, axis=0)

	vecStr = re.search(r"frame_(.*)_(.*)_", imgName, re.I|re.M).group(2)
	vec = [None] * 2
	vec[0] = float(vecStr[1])
	vec[1] = float(vecStr[4:-1])
	angle = math.ceil(np.interp(vec[1], [-1, 0, 1], [10, 67, 110]))

	pred = model.predict(processedImg)
	preded = pred[0][0]

	preded = math.ceil(np.interp(preded, [-1, 0, 1], [10, 67, 110]))

	truths.append(angle)
	preds.append(preded)

df = pd.DataFrame(columns = ["gt", "pred"])
df["gt"] = truths
df["pred"] = preds

print(df)

df.plot()
plt.show()