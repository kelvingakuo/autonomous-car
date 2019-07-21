import cv2
from keras import load_model



class TrackLane(object):
	def __init__(self):
		self.model = load_model("lane_tracker.h5")

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

		angle = self.model.predict(img)

		return angle