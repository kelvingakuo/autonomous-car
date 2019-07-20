import cv2
import glob
import time
import random

base = "saved_models/object_detection/BEST_MODEL-SO_FAR/detector_wide_angle_fullTF_7000_steps/"
cvNet = cv2.dnn.readNetFromTensorflow(base + "sorted_frozen_inference_graph.pb", base + "sorted_frozen_inference_graph.pbtxt")


labelMap = {1: "Forward", 2: "Stop", 3: "120 Kph Limit", 4: "50 Kph Limit", 5: "No Left Turn", 6: "No Right Turn", 7: "Person", 8: "Car"}
font = cv2.FONT_HERSHEY_SIMPLEX

names1 = glob.glob("test_data_for_object_detection/*.jpg")
names2 = glob.glob("test_data_for_object_detection/*.png")

names = names1 + names2

for name in names:
	start = time.time()
	img = cv2.imread(name)
	rows = img.shape[0]
	cols = img.shape[1]
	cvNet.setInput(cv2.dnn.blobFromImage(img, size=(300, 300), swapRB=True, crop=False))
	cvOut = cvNet.forward()


	for detection in cvOut[0,0,:,:]: # detection = [0, class, score, left, top, right, bottom]
		score = float(detection[2])
		if score > 0.5:
			classId = detection[1]
			if(classId == 1): # Forward - Blue
				bgr = (255, 0, 0)	
			elif(classId == 2): # Stop - Red
				bgr = (0, 51, 204)
			elif(classId == 7 or classId == 8): # Person, Car - Green
				bgr = (0, 128, 0)
			else: # Signs - Yellow
				bgr  = (0, 255, 204)

			className = labelMap[classId]
			
			left = detection[3] * cols
			top = detection[4] * rows
			right = detection[5] * cols
			bottom = detection[6] * rows

			rec = cv2.rectangle(img, (int(left), int(top)), (int(right), int(bottom)), bgr, thickness=4)
			cv2.putText(rec, className, (int(left), int(top) - 10), font, 0.7, bgr, 4 , cv2.LINE_AA)

	newName = "test_data_for_object_detection/cv_detections/" + str(random.randint(252, 8979846544)) + ".jpg"
	print("Took: {} seconds from image loading to inference".format(time.time() - start))
	cv2.imwrite(newName, img)


