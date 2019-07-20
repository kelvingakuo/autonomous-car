import numpy as np
import tensorflow as tf
import cv2
import time
import glob
import random

# Read the graph.
with tf.gfile.FastGFile("saved_models/object_detection/BEST_MODEL-SO_FAR/detector_wide_angle_fullTF_7000_steps/frozen_inference_graph.pb", "rb") as f:
	graph_def = tf.GraphDef()
	graph_def.ParseFromString(f.read())

with tf.Session() as sess:
	# Restore session
	sess.graph.as_default()
	tf.import_graph_def(graph_def, name="")

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
		inp = cv2.resize(img, (300, 300))
		inp = inp[:, :, [2, 1, 0]]  # BGR2RGB

		# Run the model
		out = sess.run([sess.graph.get_tensor_by_name("num_detections:0"),
						sess.graph.get_tensor_by_name("detection_scores:0"),
						sess.graph.get_tensor_by_name("detection_boxes:0"),
						sess.graph.get_tensor_by_name("detection_classes:0")],
					   feed_dict={"image_tensor:0": inp.reshape(1, inp.shape[0], inp.shape[1], 3)})

		# Visualize detected bounding boxes.
		num_detections = int(out[0][0])
		for i in range(num_detections):
			classId = int(out[3][0][i])
			score = float(out[1][0][i])
			bbox = [float(v) for v in out[2][0][i]]
			if score > 0.5:
				if(classId == 1): # Forward - Blue
					bgr = (255, 0, 0)	
				elif(classId == 2): # Stop - Red
					bgr = (0, 51, 204)
				elif(classId == 7 or classId == 8): # Person, Car - Green
					bgr = (0, 128, 0)
				else: # Signs - Yellow
					bgr  = (0, 255, 204)

				className = labelMap[classId]
				x = bbox[1] * cols
				y = bbox[0] * rows
				right = bbox[3] * cols
				bottom = bbox[2] * rows
				rec = cv2.rectangle(img, (int(x), int(y)), (int(right), int(bottom)), bgr, thickness = 4)
				cv2.putText(rec, className, (int(x), int(y) - 10), font, 0.7, bgr, 4 , cv2.LINE_AA)

		newName = "test_data_for_object_detection/tf_detections/" + str(random.randint(252, 8979846544)) + ".jpg"
		print("Took: {} seconds from image loading to inference".format(time.time() - start))
		cv2.imwrite(newName, img)
		# cv2.namedWindow(name, cv2.WINDOW_NORMAL)
		# cv2.resizeWindow(name, rows, cols)
		# cv2.imshow(name, img)
		# cv2.waitKey()
