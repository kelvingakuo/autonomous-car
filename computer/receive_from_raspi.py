import io
import json
import socket
import os
import pickle
import random
import struct
import sys
import time

from PIL import Image

from logs import receipts_log_config
logger = receipts_log_config.connection_logger

class StreamServer(object):
	def __init__(self, host, port):
		"""Initialise stuff
		"""
		self.host = host
		self.port = port
		self.logger = logger

		self.server =  socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		self.server.bind((self.host, self.port))

		self.logger.info('Initiliased socket on server')

		self.server.listen(0) # Server opens socket and waits for client.

		self.folder = 'computer/models/training_data/lane_following/'
		

	def receiveInstructions(self):
		""" Receive logs and instructions from client
		"""
		conn, addr = self.server.accept()
		self.logger.debug('Connected to by {}'.format(addr))
		self.logger.info('Ready to receive instructions')
		
		while True:
			txt = conn.recv(1024)
			if not txt:
				break
			self.logger.debug("{}".format(txt))

		conn.close()

	# def receiveAndSaveFrames(self):
	# 	self.logger.debug('Ready to receive frames and stuff')
	# 	conn = self.server.accept().makefile('rb')
	# 	empConn, empAddr = self.server.accept()

	# 	self.logger.info('Connected by {}'.format(empAddr))
	# 	try:
	# 		while True:
	# 			self.logger.info('Waiting for data')
	# 			# Receive image length
	# 			imgLen = struct.unpack('<L', conn.read(struct.calcsize('<L')))[0]
	# 			if not imgLen:
	# 				self.logger.info('Welp! Time to go')
	# 				break
	# 			# Create empty stream and write received contents
	# 			imgStream = io.BytesIO()
	# 			imgStream.write(conn.read(imgLen))
	# 			imgStream.seek(0)
	# 			image = Image.open(imgStream)

	# 			self.logger.info('There is image data!!!')


	# 			# actionLen = struct.unpack('<L', conn.read(struct.calcsize('<L')))[0]
	# 			# if not actionLen:
	# 			# 	break
	# 			# actionStream = io.BytesIO()
	# 			# actionStream.write(conn.read(actionLen))
	# 			# actionStream.seek(0)
				
	# 			# Read pickled actionData
	# 			# receivedPickle = empConn.recv(1024)
	# 			# action = pickle.loads(receivedPickle)
	# 			# self.logger.info(action)


	# 			# Compute img name
	# 			randItem = random.randint(5800, 7852546)
	# 			randIn = int(time.time()) + randItem
	# 			name = '{}frame_{}_.jpg'.format(self.folder, randIn)

	# 			# Write to folder
	# 			image.save(name)


	# 	finally:
	# 		conn.close()
	# 		empConn.close()
	# 		self.server.close()





if __name__ == "__main__":	
	with open('../config.json', 'rb') as fp:
		vals = json.load(fp)
	host = vals['pc']['pc_ip']
	port = vals['pc']['pc_port']

	carServer = StreamServer(host, port) 

	if(sys.argv[1] == 'boot'):
		carServer.receiveInstructions()
	elif(sys.argv[1] == 'train'):
		carServer.receiveAndSaveFrames()
	elif(sys.argv[1] == 'stream'):
		carServer.streamAnnotatedFrames()
