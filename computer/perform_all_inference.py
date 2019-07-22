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
		img = cv2.imread(theImg)
		img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
		img = cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
		img = cv2.GaussianBlur(img, (3, 3,), 0)

		angle = self.tracker_model.predict(img)

		return angle

	def generateDetections(self, theImg):
		""" Returns info about all detected objects in a frame
			Params: 
				theImg - Binary image data gotten through the wiiire
			Returns:
				detectionData - Dictionary with information about all objects detected
		"""
		img = cv2.imdecode(theImg)
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



	# def saveFrames(self, classId, ):
	# 	if(classId == 1): # Forward - Blue
	# 		bgr = (255, 0, 0)	
	# 	elif(classId == 2): # Stop - Red
	# 		bgr = (0, 51, 204)
	# 	elif(classId == 7 or classId == 8): # Person, Car - Green
	# 		bgr = (0, 128, 0)
	# 	else: # Signs - Yellow
	# 		bgr  = (0, 255, 204)

	# 	className = self.labelMap[classId]

	# 	rec = cv2.rectangle(img, (int(left), int(top)), (int(right), int(bottom)), bgr, thickness=4)
	# 			cv2.putText(rec, className, (int(left), int(top) - 10), font, 0.7, bgr, 4 , cv2.LINE_AA)

	# 	newName = "test_data_for_object_detection/cv_detections/" + str(random.randint(252, 8979846544)) + ".jpg"
	# 	print("Took: {} seconds from image loading to inference".format(time.time() - start))
	# 	cv2.imwrite(newName, img)


