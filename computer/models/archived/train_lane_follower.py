from model_definitions import lane_follower_model

import cv2
import glob
import keras
import numpy as np
import random
import re

from imgaug import augmenters
from sklearn.model_selection import train_test_split

from keras.callbacks import CSVLogger


class TrainLaneFollower(object):
	def __init__(self):
		""" Init the model to be trained
		"""
		self.model = lane_follower_model.laneFollower()
		self.lossLogs = CSVLogger('log.csv', append=True, separator=';') # Save loss history
		self.saveModelIfImprove = keras.callbacks.ModelCheckpoint(filepath = "saved_models/lane_follower_checkpoint.h5", verbose = 1, save_best_only = True) # Save model if loss improved, every epoch

	def convImg(self, img):
		""" Return image with colour channels, RGB
			Params:
				img - The image
			Returns:
				img - Channel-shifted image
		"""
		img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

		return img

	# Image augmentation
	def zoom(self, img):
		""" Return a zoomed image
			Params:
				img - The image
			Returns:
				zoomedImg - The zoomed image
		"""
		zoomer = augmenters.Affine(scale = (1, 1.5)) #150% zoom
		zoomedImg = zoomer.augment_image(img)

		return zoomedImg

	def pan(self, img):
		""" Pan L/ R/ U/ D
			Params:
				img - The image
			Returns:
				pannedImg - The panned image
		"""
		panner = augmenters.Affine(translate_percent = {'x': (0.1, 0.1), 'y': (-0.1, 0.1)})
		pannedImg = panner.augment_image(img)

		return pannedImg

	def changeBrightness(self, img):
		""" Change image brightness
			Params:
				img - The image
			Returns:
				dimmedBrighterImg - The dimmed or lit image
		"""
		brighter = augmenters.Multiply((0.7, 1.3))
		dimmedBrighterImg = brighter.augment_image(img)

		return dimmedBrighterImg


	def blur(self, img):
		""" Blur Image
			Params:
				img - The image
			Returns:
				blurredImg - The blurred image
		"""
		kernel = random.randint(1, 5)
		blurredImg = cv2.blur(img, (kernel, kernel))

		return blurredImg

	def flip(self, img, angleVector):
		""" Flip steering images and angle too
			Params:
				img - The image
				angleVector - 2x1 vector defining type of action and value [0 val] for steering
			Returns:
				flippedImg - Flipped Image
				flippedVector - Flipped angle values
		"""
		if(angleVector[0] == 0.0): #Swerve
			if(random.randint(0, 1) == 1): # Randomly flip
				flippedImg = cv2.flip(img, 1)
				angleVector[1] = 0 - angleVector[1]
				flippedVector = angleVector 
			else:
				flippedImg = img
				flippedVector = angleVector
		else:
			flippedImg = img
			flippedVector = angleVector

		return flippedImg, flippedVector


	def randomImgAugmentation(self, img, angleVector):
		""" Apply all augs to image
			Params:
				img - The image
				angleVector - 2x1 vector defining type of action and value [0 val] for steering
			Returns:
				augedImg - Augmented image
				augedVec - Augmented angle vector
		"""
		if np.random.rand() < 0.8:
			augedImg = self.pan(img)
			augedImg = self.zoom(img)
			augedImg = self.blur(img)
			augedImg = self.changeBrightness(img)
			augedImg, augedVec = self.flip(img, angleVector)
		else:
			augedImg = img
			augedVec = angleVector

		return augedImg, augedVec

	

	def preprocessForModel(self, img):
		""" Process image to what NVIDIA proposed i.e. 200x66x3 and YUV channel
			Params:
				img - The image
			Returns:
				processedImg - Processed image
		"""
		# h, w, c = img.shape
		# img = img[int(h/2): ,: ,:] # Crop top half

		# img = img / 255
		img = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
		img = cv2.GaussianBlur(img, (3, 3,), 0)
	
		processedImg = cv2.resize(img, (200, 66))

		return processedImg


	def dataAugmentation(self, imgs, angleVectors):
		""" A generator for augmented frames
		"""
		while True:
			batchImgs = []
			batchAngles = []

			for i in range(64):
				ind = random.randint(0, len(imgs) - 1)
				image = imgs[ind]
				img = self.convImg(image)

				angleVector = angleVectors[ind]

				augedImg, augedVec = self.randomImgAugmentation(img, angleVector)
				finImg = self.preprocessForModel(augedImg)

				batchImgs.append(finImg)
				batchAngles.append(augedVec)

			imgs = np.asarray(batchImgs)
			vecs = np.asarray(batchAngles)

			yield(imgs, vecs)


	def trainModel(self, XTrain, yTrain, XTest, yTest):
		""" Combine everything, train model, and save to folder
		"""
		self.model.fit_generator(self.dataAugmentation(XTrain, yTrain), steps_per_epoch = 300, epochs = 50, validation_data = self.dataAugmentation(XTest, yTest), validation_steps = 200, verbose = 1, shuffle = 1, callbacks = [self.saveModelIfImprove, self.lossLogs])

		self.model.save('saved_models/lane_follower_final.h5')


if __name__ == "__main__":
	trainFollower = TrainLaneFollower()
	
	# Load images and angles
	dataImgs = glob.glob('training_data/lane_following/*.jpg')

	imgs = []
	angleVecs = []
	for dataImg in dataImgs:
		vecStr = re.search(r'frame_(.*)_(.*)_', dataImg, re.I|re.M).group(2)
		vec = [None] * 2
		vec[0] = float(vecStr[1])
		vec[1] = float(vecStr[4:-1])

		imgs.append(cv2.imread(dataImg))
		angleVecs.append(vec)
		

	# Split into X, Y... Train and test
	XTrain, XTest, yTrain, yTest = train_test_split(imgs, angleVecs, test_size = 0.33)

	# Train and save
	trainFollower.trainModel(XTrain, yTrain, XTest, yTest)