from keras.models import Sequential
from keras.layers import Flatten 
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import Activation
from keras.layers import Conv2D
from keras.layers import MaxPooling2D
from keras.layers.normalization import BatchNormalization
from keras.optimizers import Adam

from keras import regularizers

def laneFollower():
	model = Sequential()

	model.add(Conv2D(8, (3, 3), input_shape = (120, 160, 3)))

	model.add(Activation('relu'))
	model.add(MaxPooling2D(pool_size = (2, 2)))

	model.add(Conv2D(16, (3, 3), kernel_regularizer = regularizers.l2(0.005)))
	model.add(Activation('relu'))
	model.add(MaxPooling2D(pool_size = (2, 2)))

	model.add(Conv2D(32, (3, 3), kernel_regularizer = regularizers.l2(0.005)))
	model.add(Activation('relu'))
	model.add(MaxPooling2D(pool_size = (2, 2)))

	model.add(Flatten())

	model.add(Dense(128, kernel_regularizer = regularizers.l2(0.005)))
	model.add(Activation('linear'))
	model.add(Dropout(.2))

	model.add(Dense(1, kernel_regularizer = regularizers.l2(0.005))
	model.compile(loss = "mean_squared_error", optimizer = 'adam') # Try mean_absolute_percentage_error

	return model