import cv2
import glob



dataImgs = glob.glob("test_data_for_lane_tracker/*.jpg")

cvNet = cv2.dnn.readNetFromTensorflow("model_definitions/lane_tracker/checkpoint.pb", "model_definitions/lane_tracker/checkpoint.pbtxt")

for imgName in dataImgs[0:50]:
	img = cv2.imread(imgName)
	img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
	h, w, c = img.shape
	xh = int(0.25 * h)
	img = img[xh: ,: ,:] # Crop top half
	img = cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
	img = cv2.GaussianBlur(img, (3, 3,), 0)
	processedImg = cv2.resize(img, (200, 66))

	cvNet.setInput(cv2.dnn.blobFromImage(img, size = (200, 66), swapRB = False, crop=False))
	cvOut = cvNet.forward()

	print(cvOut)