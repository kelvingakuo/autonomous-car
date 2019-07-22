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

def driveTheSelf(motor, servo, cam):
	""" 
	** Conn to relevant server
	1. Find obstacle ahead
	2. Stay on track
	3. Detect objects
	4. Return manual control whenever shit gets too real
	"""
	# Init a bunch of things
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client.connect(("ec2-3-15-24-217.us-east-2.compute.amazonaws.com", 6666))
	conn = client.makefile('wb')

	try:
		carCentre = 58
		carLeft = 95
		carRight = 15

		distance_sensing = measure_distance.MeasureDistance()
		amount = 1 # Affected by speed limit signs
		while True:
			motor.setDirection(-1)

			stream = io.BytesIO()
			# 2. Capture continuosly
			for cap in cam.capture_continuous(stream, 'jpeg', use_video_port = True):
				motor.throttle(amount)
				conn.write(struct.pack('<L', stream.tell()))
				conn.flush()
				stream.seek(0)
				conn.write(stream.read()) # Send data

				# Object detection first
				objects = pickle.loads(client.recv(4096))
				# Lane tracking next
				angle = pickle.loads(client.recv(4096))


				classes = objects["classIds"]
				lefts = objects["lefts"]
				isStopSign = any(cls == 2 for cls in classes)
				isObstacle = any((lef >= 100 and lef <= 200) for lef in lefts)
				is50Kph = any(cls == 4 for cls in classes)
				is120Kph = any(cls == 3 for cls in classes)

				if(isObstacle): # Object in the middle?
					motor.stop()
				else:
					if(isStopSign): # Stop in periphery?
						motor.stop()

				# Execute angle
				value = np.interp(angle, [carRight, carCentre, carLeft], [-1, 0, 1])
				servo.setAngle(value, 0)

				#Speed limit in periphery?
				if(is50Kph):
					amount = 0.5
				elif(is120Kph):
					amount = 1
				
				# Next
				stream.seek(0)
				stream.truncate()

	except KeyboardInterrupt:
		cam.close()

	finally:
		cam.close()
		conn.write(struct.pack('<L', 0))
		conn.close()
		client.close()


def main(motor, servo):
	cam = PiCamera()
	cam.resolution = (300, 300)
	cam.framerate = 15
	time.sleep(2)
	# Run the two functions as multiprocesses
	# proc1 = multiprocessing.Process(target = driveTheSelf, args = (motor, servo, cam, ))
	# proc2 = multiprocessing.Process(target = godMode)

	# proc1.start()
	# proc2.start()

	# proc1.join()
	# proc2.join()

	driveTheSelf(motor, servo, cam)