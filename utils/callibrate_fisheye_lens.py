# Take pics of this pattern: https://drive.google.com/file/d/0B3EXsqKhWPfdVk9NRmIzNE1RQms/view?usp=sharing with picamera to generate callibration values to deal with distortions etc
# These params are needed to avoid image distortion by the picamera
# raspistill -o %02d.jpg -t 100000 -tl 100

import cv2
import numpy as np
import glob

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1)
calibFlags = cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC + cv2.fisheye.CALIB_FIX_SKEW

# 9x6 chess board, prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objPoint = np.zeros((1, 6*9, 3), np.float32)
objPoint[0, :, :2] = np.mgrid[0:6, 0:9].T.reshape(-1, 2)

# 3d point in real world space
objPoints = []
# 2d points in image plane
imgPoints = []

images = glob.glob('callibration_data/*.jpg')
for img in images:
	image = cv2.imread(img)
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	_img_shape = gray.shape[:2]

	# find chess board corners
	ret, corners = cv2.findChessboardCorners(gray, (9, 6), cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE)

	# add object points, image points
	if(ret):
		objPoints.append(objPoint)
		cv2.cornerSubPix(gray, corners, (3, 3), (-1, -1), criteria)
		imgPoints.append(corners)

		# draw and display the corners
		cv2.drawChessboardCorners(image, (9, 6), corners, ret)
		cv2.imshow(img, image)
		cv2.waitKey(500)

# calibration
N_OK = len(objPoints)
K = np.zeros((3, 3))
D = np.zeros((4, 1))
rVecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(N_OK)]
tVecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(N_OK)]
rms, _, _, _, _ = cv2.fisheye.calibrate(
        objPoints,
        imgPoints,
        gray.shape[::-1],
        K,
        D,
        rVecs,
        tVecs,
        calibFlags,
        (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 1e-6)
    )
print("Image Dim: {}".format(str(_img_shape[::-1])))
print("{} images valid for callibration.".format(N_OK))
print("K = np.array({})".format(str(K.tolist())))
print("D = np.array({})".format(str(D.tolist())))

cv2.destroyAllWindows()