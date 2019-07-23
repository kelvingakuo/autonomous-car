import math
import numpy as np
import pickle
import pygame
import io
import socket
import struct
import sys
import time
import multiprocessing
from subprocess import call

from picamera import PiCamera
from picamera.array import PiRGBArray

from driving_instructors import measure_distance

from logs import central_log_config
logger = central_log_config.central_logger


# God mode and self_driving in separate processes.
# Shared variable to indicate when control has been handed back

def godMode():
	# Double tap 'X' to shut down everything
	pressedOnce = False 
	firstTimePress = 0

	while True:
		# 1. 'god mode'
	 	for event in pygame.event.get():
	 		if(event.type == pygame.JOYBUTTONDOWN):
	 			if(event.button == 0): # Shutdown everything
						if(pressedOnce): # Second press?
							elapsedTime = time.time() - firstTimePress
							if(elapsedTime <= 2):
								cam.close()
								logger.error("WAS DRIVING, THE DUDE SHUT US DOWN. WE GIF UP!!!")
								call("sudo killall python", shell = True)
								sys.exit()
							else:
								pressedOnce = False
								firstTimePress = 0
						else:
							pressedOnce = True
							firstTimePress = time.time()

def getPreds(motor, servo , outputQueue):
	""" 
	** Conn to relevant server
	1. Find obstacle ahead
	2. Stay on track
	3. Detect objects
	4. Return manual control whenever shit gets too real
	"""
	# Init a bunch of things
	cam = PiCamera()
	cam.resolution = (640, 480)
	cam.framerate = 15
	time.sleep(2)

	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client.connect(("ec2-3-15-154-186.us-east-2.compute.amazonaws.com", 6666))
	conn = client.makefile('wb')

	logger.info("Camera started and server connected to!!!!")

	try:
		while True:
			motor.setDirection(-1)
			rawCapture = PiRGBArray(cam, size=(640, 480))

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
				# Lane tracking next
				angle = client.recv(4096)
				angle = float(angle.decode())

				payload = {"detections": objects, "angle": angle}
				outputQueue.put(payload)
				
	except KeyboardInterrupt:
		cam.close()

	finally:
		cam.close()
		conn.close()
		client.close()


def makeDecisions(outputQueue):
	carCentre = 58
	carLeft = 95
	carRight = 15

	distance_sensing = measure_distance.MeasureDistance()
	amount = 1 # Affected by speed limit signs
	direction = -1

	motor.setDirection(direction)
	motor.throttle(amount)

	logger.info("Car starting on empty queue with default direction and speed")

	status = outputQueue.empty()
	while True: # Wait for queue
		if not outputQueue.empty():
			while True:
				# motor.setDirection(direction)
				# motor.throttle(amount)
				logger.info("Car moving at {} direction and {} speed with queue".format(direction, amount))

				payload = outputQueue.get()
				objects = payload["detections"]
				angle = payload["angle"]

				classes = objects[b"classIds"]
				lefts = objects[b"lefts"]
				isStopSign = any(cls == 2 for cls in classes)
				isObstacle = any((lef >= 100 and lef <= 200) for lef in lefts)
				is50Kph = any(cls == 4 for cls in classes)
				is120Kph = any(cls == 3 for cls in classes)


				if(isObstacle): # Object in the middle?
					logger.info("Stopping because obstacle")
					motor.stop()
					amount = 0
					direction = 0
				else:
					if(isStopSign): # Stop in periphery?
						logger.info("Stopping because stop detected")
						motor.stop()
						amount = 0
						direction = 0
				else:
					motor.setDirection(-1)
					motor.throttle(amount)

				# Execute angle
				value = np.interp(angle, [carRight, carCentre, carLeft], [-1, 0, 1])
				servo.setAngle(value, 0)

				#Speed limit in periphery?
				if(is50Kph):
					amount = 0.5
					direction = -1
				elif(is120Kph):
					amount = 1
					direction = -1


def main(motor, servo):
	q = multiprocessing.Queue()

	# Run as multiple processes
	proc1 = multiprocessing.Process(target = getPreds, args = (motor, servo, q, ))
	proc2 = multiprocessing.Process(target = makeDecisions, args = (q, ))
	proc3 = multiprocessing.Process(target = godMode)

	proc1.start()
	proc2.start()
	proc3.start()

	# proc1.join()
	# proc2.join()


	