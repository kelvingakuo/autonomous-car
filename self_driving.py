import cv2
import math
import numpy as np
import pickle
import pygame
import io
import socket
import struct
import sys
import time
from subprocess import call

from picamera import PiCamera
from picamera.array import PiRGBArray

from driving_instructors import measure_distance

from logs import central_log_config
logger = central_log_config.central_logger


# God mode and self_driving in separate processes.

# def godMode(cam):
# 	# Double tap 'X' to shut down everything
# 	pressedOnce = False 
# 	firstTimePress = 0

# 	pygame.init()
# 	stick = pygame.joystick.Joystick(0)
# 	stick = stick.init()

# 	while True:
# 		# 1. 'god mode'
# 	 	for event in pygame.event.get():
# 	 		if(event.type == pygame.JOYBUTTONDOWN):
# 	 			if(event.button == 0): # Shutdown everything
# 						if(pressedOnce): # Second press?
# 							elapsedTime = time.time() - firstTimePress
# 							if(elapsedTime <= 2):
# 								cam.close()
# 								logger.error("WAS DRIVING, THE DUDE SHUT US DOWN. WE GIF UP!!!")
# 								call("sudo killall python", shell = True)
# 								sys.exit()
# 							else:
# 								pressedOnce = False
# 								firstTimePress = 0
# 						else:
# 							pressedOnce = True
# 							firstTimePress = time.time()


def getPreds(cam, client):
	""" 
	** Conn to relevant server
	1. Find obstacle ahead
	2. Stay on track
	3. Detect objects
	4. Return manual control whenever shit gets too real
	"""
	try:
		work = True
		rawCapture = PiRGBArray(cam, size=(640, 480))
		while work:
			# 2. Capture continuosly
			for cap in cam.capture_continuous(rawCapture, format="bgr", use_video_port=True):
				img = cap.array # NP Array
				rawCapture.truncate(0)
				status, frame = cv2.imencode(".jpg", img)
				data = pickle.dumps(frame, 0)
				size = len(data)

				client.sendall(struct.pack('>L', size) + data)

				# Object detection first
				objects = pickle.loads(client.recv(4096), encoding = "bytes")
				# Lane tracking
				angle = client.recv(4096)
				angle = float(angle.decode())

				payload = {"detections": objects, "angle": angle}

				# Decisions
				yield payload
				
	except KeyboardInterrupt:
		cam.close()
		work = False

	#finally:
	#	work = False
	#	cam.close()
	#	client.close()


def makeDecisions(motor, servo, cam, client):
	carCentre = 58
	carLeft = 95
	carRight = 15

	distance_sensing = measure_distance.MeasureDistance()
	amount = 1 # Affected by speed limit signs
	direction = -1

	motor.setDirection(direction)
	motor.throttle(amount)

	logger.info("Car starting on empty queue with default direction and speed")

	drive = True
	while True:
		try:
			payload = next(getPreds(cam, client))
			objects = payload["detections"]
			angle = payload["angle"]

			classes = objects["classIds"]
			lefts = objects["lefts"]
			isStopSign = any(cls == 2 for cls in classes)
			isObstacle = any((lef >= 250 and lef <= 390) for lef in lefts)

			if(isObstacle or isStopSign): # Object in the middle or stop?
				motor.stop()
				amount = 0
				direction = 0
				continue()
			else:
				motor.setDirection(-1)
				motor.throttle(amount)

			# Execute angle
			value = np.interp(angle, [carRight, carCentre, carLeft], [-1, 0, 1])
			servo.setAngle(value, 0)

			is50Kph = any(cls == 4 for cls in classes)
			is120Kph = any(cls == 3 for cls in classes)
			#Speed limit in periphery?
			if(is50Kph):
				amount = 0.5
				direction = -1
			elif(is120Kph):
				amount = 1
				direction = -1

		except Exception as e:
			logger.error("DECISION MAKING FAILED: {}".format(e))


def main(motor, servo):
	# capture continuous just doesn't work if not in main thread.
	# Init a bunch of things
	cam = PiCamera()
	cam.resolution = (640, 480)
	cam.framerate = 15
	time.sleep(2)

	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client.connect(("ec2-3-15-154-186.us-east-2.compute.amazonaws.com", 6666))
	conn = client.makefile('wb')

	makeDecisions(motor, servo, cam, client)
	



	