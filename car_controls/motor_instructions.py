# Translating SixAxis to motor 
import numpy as np
import RPi.GPIO as GPIO


class MotorInstructions(object):
	def __init__(self):
		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)


		self.Motor1A = 4 # (Pin 7) # out Pin 6 - Motor red terminal
		self.Motor1B = 27 # (Pin 2) # out Pin 3 - Motor black terminal
		self.Motor1E = 22 # Enable


		channels = [self.Motor1A, self.Motor1B, self.Motor1E]
		GPIO.setup(channels, GPIO.OUT)

		self.pwm = GPIO.PWM(self.Motor1E, 100)
		self.pwm.start(0)

		GPIO.output(self.Motor1A, True)
		GPIO.output(self.Motor1B, False) 
 


	def throttle(self, pressed):
		""" Run the motor forward/ backward, depending on direction set, at a speed dependent on amount of button press.
			The max speed should be 100... not 75
		Params: pressed - Value of axis 5
		"""
		speed = np.interp(pressed, [-1, 1], [0, 75])
		self.pwm.ChangeDutyCycle(speed)
		GPIO.output(self.Motor1E, True)


	def stop(self):
		""" Stop motor
		"""
		# Disable
		self.pwm.ChangeDutyCycle(0)
		GPIO.output(self.Motor1A, False)
		GPIO.output(self.Motor1B, False)
		GPIO.output(self.Motor1E, False)


	def setDirection(self, value):
		""" Set the motor direction.
		Params: value - Axis value set. 	
		"""
		if(value < 0):
			# FORWARD
			GPIO.output(self.Motor1A, True)
			GPIO.output(self.Motor1B, False)
		elif(value > 0):	
			# REVERSE
			GPIO.output(self.Motor1A, False)
			GPIO.output(self.Motor1B, True)
		else:
			pass




