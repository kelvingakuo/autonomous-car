import json
import cv2
import math
import multiprocessing
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
from driving_instructors import lane_tracking

from logs import central_log_config
logger = central_log_config.central_logger

# God mode and self_driving in separate processes.

def godMode(cam, client):
	# Double tap 'X' to shut down everything
	pressedOnce = False 
	firstTimePress = 0

	pygame.init()
	stick = pygame.joystick.Joystick(0)
	stick = stick.init()

	while True:
		# 1. 'god mode'
	 	for event in pygame.event.get():
	 		if(event.type == pygame.JOYBUTTONDOWN):
	 			if(event.button == 0): # Shutdown everything
						if(pressedOnce): # Second press?
							elapsedTime = time.time() - firstTimePress
							if(elapsedTime <= 2):
								cam.close()
								client.close()
								logger.error("WAS DRIVING, THE DUDE SHUT US DOWN. WE GIF UP!!!")
								call("sudo killall python", shell = True)
								sys.exit()
							else:
								pressedOnce = False
								firstTimePress = 0
						else:
							pressedOnce = True
							firstTimePress = time.time()


def getPreds(cam, client, angleComputer):
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
				angle = angleComputer.computeSteeringAngle(img)

				payload = {"detections": objects, "angle": angle}

				# Detections 'n shii
				yield payload
				
	except KeyboardInterrupt:
		cam.close()
		client.close()
		work = False


def makeDecisions(motor, servo, cam, client):
	carCentre = 58
	carLeft = 95
	carRight = 15

	distance_sensing = measure_distance.MeasureDistance()
	steering = lane_tracking.TrackLanes()
	amount = 1 # Affected by speed limit signs
	direction = -1

	motor.setDirection(direction)
	motor.throttle(amount)

	logger.info("Car starting on empty queue with default direction and speed")

	drive = True
	while True:
		try:
			motor.setDirection(direction)
			motor.throttle(amount)
			# Ultrasonic:
			dist = distance_sensing.getDistance()
			if(dist > 0 and dist < 30):
				motor.stop()
				amount = 0
				direction = 0
				time.sleep(0.0000001)
				continue
			else:
				# Image tings
				payload = next(getPreds(cam, client, steering))
				objects = payload["detections"]
				angle = payload["angle"]

				classes = objects["classIds"]
				lefts = objects["lefts"]
				isStopSign = any(cls == 2 for cls in classes)
				isObstacle = any((lef >= 250 and lef <= 390) for lef in lefts)

				# Object detection:
				if(isObstacle or isStopSign): # Object in the middle or stop?
					motor.stop()
					amount = 0
					direction = 0
					continue
				else:
					motor.setDirection(-1)
					motor.throttle(amount)

				# Execute angle:
				if(angle !=-2):
					servo.setAngle(angle, 0)

				# Speed limit:
				is50Kph = any(cls == 4 for cls in classes)
				is120Kph = any(cls == 3 for cls in classes)
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

	with open('config.json', 'r') as fp:
			vals = json.load(fp)

	host = vals["ec2"]["ec2_host"]
	port = vals["ec2"]["ec2_port"]
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client.connect((host, port))

	# Joystick in process:
	proc = multiprocessing.Process(target = godMode, args = (cam, client, ))
	proc.start()
	proc.join()

	makeDecisions(motor, servo, cam, client)
	



	