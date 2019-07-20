import cv2
import glob
import keras
import math
import numpy as np
import os
import pandas as pd
import random
import re

from keras.preprocessing.image import ImageDataGenerator

from sklearn.model_selection import train_test_split

from model_definitions import lane_follower_v2
from model_definitions import lane_follower_model


class TrainLaneFollower(object):
	def __init__(self):
		self.model = lane_follower_model.laneFollower()
		self.lossLogs = keras.callbacks.CSVLogger('log.csv', append=True, separator=';') # Save loss history
		self.saveModelIfImprove = keras.callbacks.ModelCheckpoint(filepath = "saved_models/lane_follower_checkpoint.h5", verbose = 1, save_best_only = True) # Save model if loss improved, every epoch


	def flip(self, img, angle):
		""" Flip steering images and angle too
			Params:
				img - The image
				angle - The steering angle
			Returns:
				flippedImg - Flipped Image
				flippedAngle - Flipped angle
		"""
		if(random.randint(0, 1) >= 0.5): # Randomly flip
			flippedImg = cv2.flip(img, 1)
			if(angle == 67):
				flippedAngle = 68 # A hack
			else:
				flippedAngle = (110 - angle) + 10
		else:
			flippedImg = img
			flippedAngle = angle


		return flippedImg, flippedAngle

	def toSnipOrNotToSnip(img, dataset):
		""" Returns a snipped image depending on the dataset i.e. snips top quarter or doesn't. This was needed because camera position changed at some point
		Params:
			img - The image as loaded by CV2
			dataset - The source dataset
		Returns:
			newImg - The processed Img
		"""
		if(dataset == "old"):
			# Don't snip
			newImg = img
		else:
			# snip
			h, w, c = img.shape
			xh = int(0.25 * h)
			newImg = img[xh: ,: ,:] # Crop top quarter


		return newImg


	generator = ImageDataGenerator(
		rotation_range = 15,
		width_shift_range = 0.1,
		height_shift_range = 0.1,
		shear_range = 0.01,
		zoom_range = [0.9, 1.25],
		horizontal_flip = False,
		vertical_flip = True,
		fill_mode = 'reflect',
		data_format = 'channels_last',
		brightness_range = [0.5, 1.5]
        )

	def trainModel(self, XTrain, yTrain, XTest, yTest):
		""" Train model by fitting a data generator
			Params:
				XTrain/ XTest - Train and test input features
				yTrain/ yTest - Train and test output labels
		"""
		# self.generator.fit(XTrain)
		self.model.fit_generator(self.generator.flow(XTrain, yTrain, batch_size = 32), steps_per_epoch = len(XTrain) / 32, epochs = 200, validation_data = self.generator.flow(XTest, yTest), validation_steps = 200, verbose = 1, shuffle = 1, callbacks = [self.saveModelIfImprove, self.lossLogs])
		# For vanilla NN
		# self.model.fit(x = XTrain, y = yTrain, batch_size = 32, epochs = 200, verbose = 1, callbacks = [self.saveModelIfImprove, self.lossLogs], validation_data = (XTest, yTest))
		self.model.save('saved_models/lane_follower_final.h5')

	
if __name__ == "__main__":
	trainTracker = TrainLaneFollower()

	# Needs tonnes of memory!!!

	if(os.path.exists("training_data/lane_following_X.npy")):
		imgs = np.load("training_data/lane_following_X.npy")
		angles = np.load("training_data/lane_following_y.npy")

	else:
		imgs = []
		angles = []
		oldS = glob.glob("training_data/lane_following/lane_following_v5_good/*.jpg")
		newS = glob.glob("training_data/lane_following/lane_following_v6_good/*.jpg")
		jpgs = oldS + newS
		for dataImg in jpgs:
			vecStr = re.search(r"frame_(.*)_(.*)_", dataImg, re.I|re.M).group(2)
			vec = [None] * 2
			vec[0] = float(vecStr[1])
			vec[1] = float(vecStr[4:-1])

			angle = math.ceil(np.interp(vec[1], [-1, 0, 1], [10, 67, 110])) #Map to an actual angle

			img = cv2.imread(dataImg)

			# Flip or nah?
			dataset = re.search(r"/(.*)\\frame_", dataImg, re.I|re.M).group(1) # Check if this works
			img = trainTracker.toSnipOrNotToSnip(img, dataset)

			img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
			img = cv2.resize(img, (200, 66)) # Change this to suit the NN	

			imgs.append(img)
			angles.append(angle)


		imgs = np.array(imgs)

		# Basic preprocessing
		theMin = np.min(imgs)
		theMax = np.max(imgs)
		imgs = [cv2.cvtColor(img, cv2.COLOR_RGB2YUV) for img in imgs]
		imgs = [cv2.GaussianBlur(img, (3, 3,), 0) for img in imgs]
		imgs = [(img - theMin) / (theMax - theMin) for img in imgs] # Normalise

		# Flip at random, then add to dataset
		j = 0
		flippedImgs = []
		flippedAngles = []
		while(j < len(imgs)):
			img = imgs[j]
			ang = angles[j]

			fImg, fAng = trainTracker.flip(img, ang)

			if(fAng == ang):
				pass
			else:
				flippedImgs.append(fImg)
				flippedAngles.append(fAng)

			j = j + 1

		angles = angles + flippedAngles
		imgs = imgs + flippedImgs
		
		angles = np.array(angles)
		imgs = np.array(imgs)

		# Save
		np.save("training_data/lane_following_X.npy", imgs)
		np.save("training_data/lane_following_y.npy", angles)


	# For vanilla NN
	#imgs = imgs.flatten().reshape(imgs.shape[0], -1)


	# Split into X, Y... Train and test
	XTrain, XTest, yTrain, yTest = train_test_split(imgs, angles, test_size = 0.33)

	# Train
	trainTracker.trainModel(XTrain, yTrain, XTest, yTest)

