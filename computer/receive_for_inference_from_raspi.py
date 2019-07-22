import cv2
import io
import socket
import struct
import time
import pickle
import numpy as np

import perform_all_inference


# Receive a frame, detect object and predict steering angle, and return

if __name__ == "__main__":
	inferer = perform_all_inference.Infer()

	host = '0.0.0.0'
	port = 6666

	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.bind((host, port))
	server.listen(1)

	conn, addr = server.accept()
	print("Connected to by: {} {}".format(conn, addr))
	# fil = conn[0].makefile('rb')
	try:
		while True:
			# image_len = struct.unpack('<L', fil.read(struct.calcsize('<L')))[0]
			# if not image_len:
			# 	break
			# img = io.BytesIO()
			# img.write(fil.read(image_len))
			# img.seek(0)

			# img = np.fromstring(img.getvalue(), dtype=np.uint8)

			data = b""
			size = struct.calcsize(">L")
			print(size)
			while True:
				while (len(data) < size):
					data += conn.recv(4096)

				msgSizePacked = data[:size]
				data = data[size:]
				msgSize = struct.unpack(">L", msgSizePacked)[0]
				while(len(data) < msgSize):
					data+=conn.recv(4096)

				frameData = data[:msgSize]
				data = data[msgSize:]

				img = pickle.loads(frameData, fix_imports=True, encoding="bytes")
				
				detection = inferer.generateDetections(img)
				payload = pickle.dumps(detection)
				conn.sendall(payload) #This most probably doesn't work

				angle = inferer.generateAngle(img)
				payload = pickle.dumps(angle)
				conn.sendall(angle)

	finally:
		conn.close()
		server.close()



