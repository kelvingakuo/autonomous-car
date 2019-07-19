import cv2
import matplotlib.pyplot as plt
import math
import numpy as np
import re



path = "test_data_for_preprocessing/frame_1561353688_[0, 0.814447462385937]_.jpg"
# path = "test_data_for_preprocessing/frame_1561415973_[0, -1.000030518509476]_.jpg"
img = cv2.imread(path)

vecStr = re.search(r"frame_(.*)_(.*)_", path, re.I|re.M).group(2)
vec = [None] * 2
vec[0] = float(vecStr[1])
vec[1] = float(vecStr[4:-1])

angle = math.ceil(np.interp(vec[1], [-1, 0, 1], [10, 67, 110])) #Map to an actual angle
ang = "Steering angle : {}".format(angle)
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

plt.imshow(img)
plt.title(ang)
plt.show()

h, w, c = img.shape
xh = int(0.25 * h)
img = img[xh: ,: ,:] # Crop top half

plt.imshow(img)
plt.title(ang)
plt.show()

# theMin = np.min(imgs)
# theMax = np.max(imgs)
img = cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
img = cv2.GaussianBlur(img, (3, 3,), 0)


flippedImg = cv2.flip(img, 1)
if(angle == 67):
	angle = 68 # A hack
else:
	angle = (110 - angle) + 10


ang = "Steering angle after flipping: {} degrees".format(angle)
plt.imshow(flippedImg)
plt.title(ang)
plt.show()
