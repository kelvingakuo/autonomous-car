# All sixaxis commands are gotten and routed from here
import logging
import pickle
import pygame
import socket
import sys
import time

from gpiozero import LED
from subprocess import call

import self_driving as driveTheSelf
import save_frames

from car_controls import servo_instructions
from car_controls import motor_instructions
from connections import stream_to_pc
from logs import central_log_config
logger = central_log_config.central_logger


class ControlTower(object):
	""" Central car control
	"""
	def __init__(self, circServoInstrs = None, circMotorInstrs = None, circStick = None, circConn = None, circSave = None, circCtrLED = None, circConnLED = None,  isCircular = False):

		# if(isCircular): # A circular reference from self_driving to enable return of manual control at any time!!
		# 	self.isTraining = True
		# 	self.wasDriving = True
		# 	self.ctrLED = circCtrLED
		# 	self.connLED = circConnLED
		# 	self.servoInstrs = circServoInstrs
		# 	self.motorInstrs = circMotorInstrs
		# 	self.stick = circStick
		# 	self.connToServer = circConn
		# 	self.saveData = circSave
		# 	self.driveTheSelf = self_driving.SelfDrive(circServoInstrs, circMotorInstrs, circStick, circConn, circSave, circCtrLED, circConnLED)
		# 	self.ctrLED.on()
		# 	self.connLED.on()

		# else:
		self.isTraining = False
		self.wasDriving = False
		self.ctrLED = LED(23)
		self.connLED = LED(24)
		self.workingLED = LED(14) # Program has booted
		self.workingLED.blink()
		self.servoInstrs = servo_instructions.ServoInstructions()
		self.motorInstrs = motor_instructions.MotorInstructions()
		time.sleep(8) # Wait for steady light on SixAxis Ctrler
		self.stick = self.connSixAxis(self.ctrLED)
		self.connToServer = self.connToServer(self.connLED)
		self.saveData = save_frames.SaveFrames()
		self.ctrLED.on()
		self.connLED.on()


		
	def connToServer(self, led):
		try:
			led.blink()
			logger.debug('Trying to connect to server...')
			connection = stream_to_pc.StreamClient()
			logger.debug('SUCCESSFULLY CONNECTED TO SERVER')
			led.off()
			return connection
		except socket.error as e:
			logger.error("ERROR CONNECTING TO SERVER. REASON FOR FAILURE {}. \nTrying again...".format(e))
			time.sleep(2) #Recheck every 2 seconds
			self.connToServer(led)


	def connSixAxis(self, led):
		led.blink()
		pygame.init()
		count = pygame.joystick.get_count()
		if(count == 0):
			logger.error('Make sure the joystick is connected')
			time.sleep(2) #Recheck every 2 seconds
			pygame.quit()
			self.connSixAxis(led)
		else:			
			logger.debug("Installed {} joystick".format(count))
			stick = pygame.joystick.Joystick(0)
			led.off()
			stick = stick.init()

			return stick


	def main(self):
		servoInstrs = self.servoInstrs
		motorInstrs = self.motorInstrs
		stick = self.stick
		saveData = self.saveData

		pressedOnce = False # Double tap 'X' to terminate things
		firstTimePress = 0

		# Choose what to do
		self.isChoiceTime = True
		self.isDriving = False
		self.isSaveTime = False
		self.stoppedTraining = 5 # Five training sessions ONLY
		self.noPress = True

		if(self.wasDriving):
			self.connToServer.sendInstructions("Control returned. DRIVE!!!!")
		else:
			if(self.stoppedTraining == 5):
				self.connToServer.sendInstructions("Press 'O' for self_driving or 'A' for training")
			else:
				self.connToServer.sendInstructions("Press 'O' for self_driving or 'A' for training or nothing to play around with car!!!")

		done = False
		while not done:
			try:
				for event in pygame.event.get():
						if(event.type == pygame.QUIT):
							done = True
								
						elif((event.type == pygame.JOYAXISMOTION)  and (self.isTraining)):
							self.noPress = False
							if(event.axis == 0): # Steer car instruction
								logger.info("Car swerve. Amount: {}".format(event.value))
								servoInstrs.setAngle(event.value, 0) # Actually turn the car
								if(self.isSaveTime):
									saveData.saveFrame(0, event.value) # Save the frame and steering amount
								
							elif(event.axis == 3): #Pan
								logger.info("Cam pan. Amount: {}".format(event.value))
								servoInstrs.setAngle(event.value, 3)

							#Motor
							elif(event.axis == 5):
								logger.info("Motor throttle. Amount: {}".format(event.value))
								motorInstrs.throttle(event.value)
								if(self.isSaveTime):
									saveData.saveFrame(1, event.value)
								
							elif(event.axis == 4):
								logger.info("Direction change")
								motorInstrs.setDirection(event.value)
								if(self.isSaveTime):
									if(event.value < 0): # Forward
										saveData.saveFrame(4, 0)
									else: #Backward
										saveData.saveFrame(3, 0)
								
												
						elif(event.type == pygame.JOYBUTTONDOWN):
							self.noPress = False
							if(event.button == 11 and (self.isTraining)):
								servoInstrs.alignCentre()

							elif(event.button == 5 and (self.isTraining)):
								logger.info("Car stopping")
								motorInstrs.stop()
								if(self.isSaveTime):
									saveData.saveFrame(2, 0)
								

							elif(event.button == 2):
								if(self.isChoiceTime and (self.stoppedTraining > 0)):
									# Training
									logger.info("Chose to train")
									self.saveData.initCam()
									self.isTraining = True
									self.isSaveTime = True
									self.wasDriving = False
								
									self.connToServer.sendInstructions("You chose to collect training data. You have {} training sessions left\n".format(self.stoppedTraining))
									self.connToServer.sendInstructions("To collect data: \n")
									self.connToServer.sendInstructions("1. Drive the car around on the track for whatever amount of time\n")
									self.connToServer.sendInstructions("2. Double tap 'X' to terminate\n")
									self.connToServer.sendInstructions("3. Copy 'computer/models/training_data/lane_following' from the Raspi to get the data")

							elif(event.button == 1):
								if(self.isChoiceTime):
									# Self-driving
									logger.info("Chose self-driving")
									self.saveData.closeCam()
									self.connToServer.sendInstructions("The car is now independent. Goodbye!!\n")
									# Let's drive ourselves
									self.ctrLED.off()
									self.connLED.off()
									done = True
									self.connToServer.shutThingsDown()
									driveTheSelf.main(motorInstrs, servoInstrs) # No manual control. Can only shut down

						

							elif(event.button == 0): # Shutdown everything
								if(pressedOnce): # Second press?
									elapsedTime = time.time() - firstTimePress
									if(elapsedTime <= 2 and (self.isTraining) and (self.stoppedTraining > 0)):
										self.isSaveTime = False
										self.saveData.closeCam()
										logger.error("STOPPED SAVING TRAINING DATA!!")
										self.stoppedTraining = self.stoppedTraining - 1
										self.connToServer.sendInstructions("Halted data collection!!")
										self.connToServer.sendInstructions("Press 'O' for self_driving or 'A' for training")
										
									elif(elapsedTime <= 2 and (self.isTraining) and (self.stoppedTraining == 0)):
										self.ctrLED.off()
										self.connToServer.sendInstructions("SORRY. THAT'S ALL THE TIME WE HAD!!!\n")
										self.connToServer.sendInstructions("SHUTTING EVERYTHING DOWN!!! GOODBYE!!!")
										logger.error("SHUTTING EVERYTHING DOWN")
										# call("sudo shutdown now", shell = True)
										sys.exit() # Terminate program	


									elif(elapsedTime > 2):
										pressedOnce = False
										firstTimePress = 0
								else:
									pressedOnce = True
									firstTimePress = time.time()

							
						elif(event.type == pygame.JOYBUTTONUP and (self.isTraining)):
							self.noPress = False
							if(event.button == 11):
								servoInstrs.alignCentre()

				self.noPress = True
				if(self.isSaveTime and self.noPress):
					saveData.saveFrame(0, 0)
								
			except KeyboardInterrupt:
				pass


if __name__ == "__main__":
	central = ControlTower()
	central.main()
