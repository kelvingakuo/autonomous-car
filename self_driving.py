import pygame
import sys
import time

from picamera import PiCamera

from driving_instructors import measure_distance

from logs import central_log_config
logger = central_log_config.central_logger


class SelfDrive(object):
	""" Drives car using a bunch of stuff
	"""
	def __init__(self, servo, motor, stick, connection, saving, ctrl, conn):
		""" 1. Load models
			2. Initiate stuff
		"""
		self.lane_follower = ''
		self.object_detector = ''
		self.distance_sensing = measure_distance.MeasureDistance()

		# Circular reference tings
		self.servo = servo
		self.motor = motor
		self.stick = stick
		self.serverConn = connection
		self.save = saving
		self.ctrl = ctrl
		self.conn = conn


	def  main(self):
		""" 1. Find obstacle ahead
			2. Stay on track
			3. Detect objects
			4. Return manual control whenever shit gets too real
		"""
		# Init a bunch of things
		self.motor.setDirection(-1)
		self.motor.throttle(1)

		self.cam = PiCamera()
		self.cam.resolution = (640, 480)


		# Double tap 'X' to regain manual control
		pressedOnce = False 
		firstTimePress = 0

		while True:
			# 1. Implementing 'god mode'
		 	for event in pygame.event.get():
		 		if(event.type == pygame.JOYBUTTONDOWN):
		 			if(event.button == 0): # Shutdown everything
							if(pressedOnce): # Second press?
								elapsedTime = time.time() - firstTimePress
								if(elapsedTime <= 2):
									self.cam.close()
									import control_tower
									circularRef = control_tower.ControlTower(self.servo, self.motor, self.stick, self.serverConn, self.save, self.ctrl, self.conn, isCircular = True)
									logger.error("RETURNING MANUAL CONTROL")
									circularRef.main()	
								else:
									pressedOnce = False
									firstTimePress = 0
							else:
								pressedOnce = True
								firstTimePress = time.time()


			# 2. Detecting obstacle ahead
			time.sleep(0.00001)
			dist = self.distance_sensing.getDistance()
			if((dist > 0) and (dist <= 10)): # Increase distance? Change sensor placement?
				logger.error("OBSTACLE DETECTED AT {} CMS".format(dist))
				self.motor.stop()
				logger.info("WAITING")
				time.sleep(5) # Wait to see if obstacle has moved

			else:
				logger.info("NO OBSTACLE. DRIVING!")
				# Driving forward, full throttle
				self.motor.setDirection(-1)
				self.motor.throttle(1)


			# 3. Staying on track
				