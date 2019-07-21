from keras.models import Sequential
from keras.layers import Flatten 
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import Activation
from keras.layers import Conv2D
from keras.layers import MaxPooling2D
from keras.layers.normalization import BatchNormalization
from keras.optimizers import Adam
import os
from keras.models import load_model



def laneFollower():
	""" The lane following CNN inspired by: https://arxiv.org/pdf/1604.07316.pdf
	"""
	if(os.path.exists("../saved_models/lane_follower_final.h5")):
		model = load_model("../saved_models/lane_follower_final.h5")
	else:
		model = Sequential()

		model.add(Conv2D(24, (5,5), strides = (2,2), input_shape = (66, 200, 3)))
		model.add(Activation("elu")) # Training is being done with Relu

		model.add(Conv2D(36, (5, 5), strides = (2, 2))) 
		model.add(Activation("elu"))
		model.add(Conv2D(48, (5, 5), strides = (2, 2))) 
		model.add(Activation("elu"))
		model.add(Conv2D(64, (3, 3)))
		model.add(Activation("elu")) 
		model.add(Dropout(0.2)) # Not in original paper
		model.add(Conv2D(64, (3, 3))) 
		model.add(Activation("elu"))


		model.add(Flatten())
		model.add(Dropout(0.2)) # Not in original paper
		model.add(Dense(100))
		model.add(Activation("elu"))
		model.add(Dense(50))
		model.add(Activation("elu"))
		model.add(Dense(10))
		model.add(Activation("elu"))

		model.add(Dense(1)) # Left: 10, Straight: 67, Right: 110
		optim = Adam(lr = 1e-3) # Try decay = 1e-3 /200
		model.compile(loss = "mean_squared_error", optimizer = "adam") # Try mean_absolute_percentage_error

	return model


