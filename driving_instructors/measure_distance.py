# Measure distance using ultrasonic sensor
# https://raspberrypi.stackexchange.com/a/89287
from nanpy import Ultrasonic

class MeasureDistance(object):
	def __init__(self):
		self.echoPin = 7
		self.trigPin = 9
		self.ultra = Ultrasonic(self.echoPin, self.trigPin, useInches = False)


	def getDistance(self):
		""" Measure distance to obstacle in centimetres
			Returns:
				cms - Distance in centimetres
		"""
		return self.ultra.get_distance()