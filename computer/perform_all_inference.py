import cv2
import glob
import time
import random
import cv2
from keras.models import load_model


class Infer(object):
	def __init__(self):
		self.cvNet = cv2.dnn.readNetFromTensorflow("cv_sorted_frozen_inference_graph.pb", "cv_sorted_frozen_inference_graph.pbtxt")
		self.labelMap = {1: "Forward", 2: "Stop", 3: "120 Kph Limit", 4: "50 Kph Limit", 5: "No Left Turn", 6: "No Right Turn", 7: "Person", 8: "Car"}
		self.font = cv2.FONT_HERSHEY_SIMPLEX
		self.tracker_model = load_model("lane_tracker.h5")

	def generateAngle(self, theImg):
		""" Takes the binary image and runs the lane tracker NN on it to generate the steering angle
			Params:
				theImg - Binary image received through the wiiire
			Returns:
				angle - The predicted angle
		"""
		img = cv2.imdecode(theImg, cv2.IMREAD_COLOR)
		img = cv2.resize(img, (200, 66))
		img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
		img = cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
		img = cv2.GaussianBlur(img, (3, 3,), 0)
		img = np.expand_dims(img, axis=0)

		angle = self.tracker_model.predict(img)
		angle = angle[0][0]

		return angle

	def generateDetections(self, theImg):
		""" Returns info about all detected objects in a frame
			Params: 
				theImg - Binary image data gotten through the wiiire
			Returns:
				detectionData - Dictionary with information about all objects detected
		"""
		img = cv2.imdecode(theImg, cv2.IMREAD_COLOR)
		rows = img.shape[0]
		cols = img.shape[1]
		self.cvNet.setInput(cv2.dnn.blobFromImage(img, size=(300, 300), swapRB = True, crop=False))
		cvOut = self.cvNet.forward()

		detectionData = dict()
		detectionData["classIds"] = []
		detectionData["lefts"] = []
		detectionData["tops"] = []
		detectionData["rights"] = []
		detectionData["bottoms"] = []

		for detection in cvOut[0,0,:,:]: # detection = [0, class, score, left, top, right, bottom]
			score = float(detection[2])
			print(score)
			if score > 0.5:
				classId = detection[1]
				left = detection[3] * cols
				top = detection[4] * rows
				right = detection[5] * cols
				bottom = detection[6] * rows

				detectionData["classIds"].append(classId)
				detectionData["lefts"].append(left)
				detectionData["tops"].append(top)
				detectionData["rights"].append(right)
				detectionData["bottoms"].append(bottom)

		return detectionData

