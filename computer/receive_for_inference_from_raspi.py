import cv2
import io
import socket
import struct
import time
import pickle

import perform_all_inference


# Receive a frame, detect object and predict steering angle, and return

if __name__ == "__main__":
	inferer = perform_all_inference.Infer()

	host = '0.0.0.0'
	port = 6666

	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.bind((host, port))
	server.listen(1)

	conn = server.accept()[0].makefile('rb')
	try:
		while True:
			image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
			if not image_len:
				break
			img = io.BytesIO()
			img.write(connection.read(image_len))
			img.seek(0)

			detection = inferer.generateDetections(img)
			payload = pickle.dumps(detection)
			conn.sendall(payload) #This most probably doesn't work

			angle = inferer.generateAngle(img)
			payload = pickle.dumps(angle)
			conn.sendall(angle)

	finally:
		connection.close()
		server_socket.close()



