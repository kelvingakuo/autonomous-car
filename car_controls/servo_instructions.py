# Car: D6
# Cam L/R: D2

# car angles: 15, 95, 132
# pan angles: 0, 75, 180


import math
from nanpy import Servo
import numpy as np


class ServoInstructions(object):
	def __init__(self):
		self.carServo = Servo(6)
		self.panServo = Servo(2)

		self.carCentre = 58
		self.carLeft = 95
		self.carRight = 15
		self.panCentre = 75

		self.alignCentre()
		

	def setAngle(self, value, what):
		""" Move servo to an angle based on axis value
		Params: value - Amount tilted 
				what - Axis used (To determine servo)
		"""
		if(what == 0): #Car, pan concurrent
			if(value != 0):
				angle1 = math.ceil(np.interp(value, [-1, 0, 1], [self.carRight, self.carCentre, self.carLeft]))
				# angle2 = math.ceil(np.interp(value, [-1, 0, 1], [140, 75, 28]))
			else:
				angle1 = self.carCentre
				# angle2 = 75
			
			self.carServo.write(angle1)
			# self.panServo.write(angle2)

		elif(what == 3): #Pan
			if(value != 0):
				angle = math.ceil(np.interp(value, [-1, 0, 1], [140, 75, 0])) # Servo was installed backwards
			else:
				angle = 75

			self.panServo.write(angle)

		
	def alignCentre(self):
		""" Align all servos to predefined centres
		"""
		self.carServo.write(self.carCentre)
		self.panServo.write(self.panCentre)
		






		




