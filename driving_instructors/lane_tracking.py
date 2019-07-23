import cv2
import glob
import math
import numpy as np




class TrackLanes(object):
	def __init__(self):
		self.maskLow = (0,0,102)
		self.maskHigh = (179,255,255)
		self.currentAngle = 0

	def makePoints(self, img, line):
		height, width, _ = img.shape
		slope, intercept = line
		y1 = height  # bottom of the img
		y2 = int(y1 * 1 / 2)  # make points from middle of the img down
		x1 = max(-width, min(2 * width, int((y1 - intercept) / slope)))
		x2 = max(-width, min(2 * width, int((y2 - intercept) / slope)))

		return [[x1, y1, x2, y2]]

	def computeLines(self, img):
		""" Computes the complete lane by combining the segments detected, by computing slopes 'n shii
			If all line slopes are < 0: then we only have detected left lane
			If all line slopes are > 0: then we only have detected right lane

			Params:
				img - The image loaded by CV2 in the original format
			Returns:
				actualLanes - The actual lanes
		"""
		lane_lines = []
		if line_segments is None:
			return lane_lines

		height, width, _ = img.shape
		left_fit = []
		right_fit = []

		boundary = 1/4
		left_region_boundary = width * (1 - boundary)  # left lane line segment should be on left 2/3 of the screen
		right_region_boundary = width * boundary # right lane line segment should be on left 2/3 of the screen

		for line_segment in line_segments:
			for x1, y1, x2, y2 in line_segment:
				if x1 == x2:
					continue
				fit = np.polyfit((x1, x2), (y1, y2), 1)
				slope = fit[0]
				intercept = fit[1]
				if slope < 0:
					if x1 < left_region_boundary and x2 < left_region_boundary:
						left_fit.append((slope, intercept))
				else:
					if x1 > right_region_boundary and x2 > right_region_boundary:
						right_fit.append((slope, intercept))

		left_fit_average = np.average(left_fit, axis=0)
		if len(left_fit) > 0:
			lane_lines.append(self.makePoints(img, left_fit_average))

		right_fit_average = np.average(right_fit, axis=0)
		if len(right_fit) > 0:
			lane_lines.append(self.makePoints(img, right_fit_average))

		return actualLanes
			
	def detectEdges(self, hsv, img):
		""" Returns the canny edge, Hough Transformed detected lines
			Params:
				hsv - The image as loaded by CV2 in HSV colour space
				img - The image as loaded by CV2 in original form
			Returns:
				lineSegs - The lines as detected
		"""
		mask = cv2.inRange(hsv, self.maskLow, self.maskHigh)
		mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel=np.ones((8,8),dtype=np.uint8))
		mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel=np.ones((20,20),dtype=np.uint8))
		mask = cv2.morphologyEx(mask, cv2.MORPH_ERODE, kernel=np.ones((5,5),dtype=np.uint8))

		road_hsv = cv2.bitwise_and(hsv, hsv,mask=mask)
		mask2 = cv2.inRange(road_hsv, self.maskLow, self.maskHigh)
		result = cv2.bitwise_and(img, img,mask = mask2)

		edges = cv2.Canny(mask, 200, 400)
		maskedResult = cv2.bitwise_and(edges, edges, mask = mask)

		rho = 1
		angle = np.pi / 180
		min_threshold = 10
		lineSegs = cv2.HoughLinesP(edges, rho, angle, min_threshold, np.array([]), minLineLength=8, maxLineGap=4)	

		return lineSegs

	def computeSteeringAngle(self, img):
		""" Returns a steering angle between 15 and 95 degrees
			Params:
				img - The image array from PiCamera
			Returns:
				angle - Value to directly pass to the servo instructor
		"""
		jpg = cv2.imread(img)

		h, w, c = jpg.shape
		xh = int(0.4 * h)
		img = jpg[xh: ,: ,:] # Crop top quarter
		hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

		lineSegs = self.detectEdges(hsv, img)
		theActualLanes = self.computeLines(img, lineSegs)

		h, w, _ = img.shape
		if(len(theActualLanes) == 0):
			angle = -2 # No action
		else:
			if (len(theActualLanes) == 1):
				x1, _, x2, _ = theActualLanes[0][0]
				x_offset = x2 - x1
			else:
				_, _, left_x2, _ = theActualLanes[0][0]
				_, _, right_x2, _ = theActualLanes[1][0]
				camera_mid_offset_percent = 0.02 # 0.0 means car pointing to center, -0.03: car is centered to left, +0.03 means car pointing to right
				mid = int(w / 2 * (1 + camera_mid_offset_percent))
				x_offset = (left_x2 + right_x2) / 2 - mid

			# find the steering angle, which is angle between navigation direction to end of center line
			y_offset = int(h / 2)

			angle_to_mid_radian = math.atan(x_offset / y_offset)  # angle (in radian) to center vertical line
			angle_to_mid_deg = int(angle_to_mid_radian * 180.0 / math.pi)  # angle (in degrees) to center vertical line
			predAngle = angle_to_mid_deg + 90  # this is the steering angle needed by picar front wheel
			angle = math.ceil(np.interp(predAngle, [0, 90, 180], [-1, 0, 1])) # Map to a value for the servo

		angle = self.smootherTurns(angle, len(theActualLanes))

		return angle


	def smootherTurns(self, prededAngle, lines):
		""" To avoid 'bouncy' turns, decided whether or not to deviate by that much, based on previous values
			Params: 
				prededAngle - Value preded by self.computeSteeringAngle
				lines - Number of lines detected
			Returns:
				angle - The actual value
		"""
		if(prededAngle == -2):
			angle = prededAngle
		else:
			if(lines == 2):
				maxDev = 5
			else:
				maxDev = 1

			angleDev = prededAngle - self.currentAngle
			if(abs(angle) > maxDev):
				angle = int(self.currentAngle + (maxDev *  angleDev / abs(angleDev)))
			else:
				angle = prededAngle

		self.currentAngle = angle

		return angle

