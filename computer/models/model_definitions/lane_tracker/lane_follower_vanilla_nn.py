from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import Activation
from keras.models import Sequential

def laneFollower():
	""" A super simple vanilla feed-forward NN
	"""
	model = Sequential()
	model.add(Dense(3200, input_shape = (39600, ), kernel_initializer='glorot_uniform'))
	model.add(Dropout(0.2))
	model.add(Activation('elu'))	

	model.add(Dense(320, kernel_initializer='normal'))
	model.add(Activation('elu'))

	model.add(Dense(32, kernel_initializer='normal'))
	model.add(Activation('elu'))

	model.add(Dense(1))
	model.compile(loss = "mean_squared_error", optimizer = 'adam')

	return model