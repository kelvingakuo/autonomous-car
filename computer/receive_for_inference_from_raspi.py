import cv2
import io
import socket
import struct
import time
import pickle

import detect_objects
import track_lane


# Receive a frame, detect object and predict steering angle, and return

if __name__ == "__main__":
	detector = detect_objects.DetectObjects()
	tracker = track_lane.TrackLane()

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

			detection = detector.generateDetections(img)
			payload = pickle.dumps(detection)
			conn.sendall(payload) #This most probably doesn't work

			angle = tracker.generateAngle(img)
			payload = pickle.dumps(angle)
			conn.sendall(angle)

	finally:
		connection.close()
		server_socket.close()



