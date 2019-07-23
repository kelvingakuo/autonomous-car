# Save (frame, angleVector) as frame_vec_.jpg e.g. frame_timestamp_[0, -1]_.jpg in computer/models/training_data/lane_following
# This data is used to train the lane following CNN

# Output vectors:
# out = np.array([0, val])
# out.shape = (2, 1)
# Car turn -> [0, val]
# Motor throttle -> [1, val]
# Stop -> [2, 0]
# Backward gear -> [3, 0]
# Forward gear -> [4, 0]
# 'val' is the axis value in range (-1 to +1)

from picamera import PiCamera
from subprocess import call
import time
import random


class SaveFrames(object):
	def __init__(self):
		# Clean up
		call("sudo rm -rf computer/models/training_data/lane_following", shell = True)
		call("sudo mkdir computer/models/training_data/lane_following", shell = True)

		self.camera = PiCamera()

	def initCam(self):
		self.camera.resolution = (640, 480)


	def closeCam(self):
		try:
			self.camera.close()
		except AttributeError:
			pass

	def saveFrame(self, action, value):
		""" Takes picture of current view, computes name and saves in computer/models/training_data/lane_following
			Params:
				action - Value repping the action e.g. 0 for car turn
				value - Amount of axis, button press etc
		"""
		folder = 'computer/models/training_data/lane_following/' #Where to save to 

		# Create name
		randItem = random.randint(5800, 7852546)
		randIn = int(time.time()) + randItem

		name = '{}frame_{}_{}_.jpg'.format(folder, randIn, [action, value]) # Save steering amount in name of image #VeryClever
		# Capture and save
		self.camera.capture(name, use_video_port = True) # Take pic
	



