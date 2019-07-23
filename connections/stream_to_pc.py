import io
import json
import logging
import pickle
import socket
import struct
import time


import time
import random


class StreamClient(object):
	def __init__(self):
		"""Initialise stuff
		"""
		with open("config.json", "r") as fp:
			vals = json.load(fp)

		self.host = vals["pc"]["pc_ip"]
		self.port = vals["pc"]["pc_port"]

		self.client =  socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		self.client.connect((self.host, self.port)) # Client connects to server

		# self.camera = PiCamera()
		# self.camera.resolution = (640, 480)



	def sendInstructions(self, instructions):
		""" Sends logs and instructions to the server.
			Run "receiveInstructions()" on server
		"""
		self.client.sendall(instructions.encode())


	# def sendFrameToServer(self, action, value):
	# 	""" Takes picture of current view, generates stream and sends. It also sends the action as a stream
	# 		Params:
	# 			action - Value repping the action e.g. 0 for car turn
	# 			value - Amount of axis, button press etc
	# 		Run "receiveAndSaveFrames ()" on server
	# 	"""
	# 	self.conn = self.client.makefile("wb")

	# 	imgStream = io.BytesIO()
	# 	# actionStream = io.BytesIO()
	# 	pickledAction = pickle.dumps([action, value])

	# 	self.camera.capture(imgStream, format="jpeg", use_video_port=True)

	# 	# Send image length
	# 	imgLen = imgStream.tell()
	# 	self.conn.write(struct.pack("<L", imgLen))
	# 	# Send image
	# 	self.conn.flush()
	# 	imgStream.seek(0)
	# 	self.conn.write(imgStream.read())
	# 	# Reset
	# 	imgStream.seek(0)
	# 	imgStream.truncate()

	# 	# Send action dump
	# 	self.client.send(pickledAction)


	# 	# # Send action length
	# 	# actionLen = actionStream.tell()
	# 	# self.conn.write(struct.pack("<L", actionLen))
	# 	# # Send action
	# 	# self.conn.flush()
	# 	# actionStream.seek(0)
	# 	# self.conn.write(actionStream.read())
	# 	# # Reset
	# 	# actionStream.seek(0)
	# 	# actionStream.truncate()




	# def closeDataStream(self):
	# 	""" Closes the training data stream
	# 	"""
	# 	self.conn.write(struct.pack("<L", 0)) # Tell server we"re done with data streaming
	# 	self.conn.close()


	def shutThingsDown(self):
		""" Closes the client connection entirely
		"""
		self.client.close()

