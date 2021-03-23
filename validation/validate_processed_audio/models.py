from tensorflow.keras.models import Sequential 
from tensorflow.keras.layers import Dense, Conv2D, Flatten, MaxPooling2D
from tensorflow.keras.optimizers import SGD, Adam


opt_list = {"sgd":SGD, "adam":Adam}


def LR(input_dim, opt, lr):
	opt = opt_list[opt](lr=lr)
	model = Sequential(name="FC_model")
	model.add(Dense(2, input_dim=input_dim, activation='softmax'))
	model.compile(optimizer=opt, loss='binary_crossentropy', metrics=['accuracy']) 
	model.summary()
	return model


def CNN_1(input_shape, num_filters, opt, lr):
	opt = opt_list[opt](lr=lr)
	model = Sequential(name="CNN_model_1")
	model.add(Conv2D(filters=16, kernel_size=(num_filters,5), strides=1, input_shape=input_shape, activation='relu'))
	# model.add(Conv2D(filters=16, kernel_size=(num_filters,5), strides=1, input_shape=input_shape, activation='linear'))
	# model.add(Conv2D(filters=16, kernel_size=(num_filters,5), strides=1, input_shape=input_shape, activation='sigmoid'))
	# model.add(Conv2D(filters=8, kernel_size=(num_filters,5), strides=1, input_shape=input_shape, activation='relu'))
	model.add(Flatten())
	model.add(Dense(2, activation='softmax'))
	model.compile(optimizer=opt, loss='binary_crossentropy', metrics=['accuracy']) 
	model.summary()
	# A	
	return model


def CNN_2(input_shape, num_filters, opt, lr):
	opt = opt_list[opt](lr=lr)
	model = Sequential(name="CNN_model_2")
	model.add(Conv2D(filters=32, kernel_size=4, strides=1, input_shape=input_shape, activation='relu'))
	model.add(Conv2D(filters=16, kernel_size=2, strides=1, activation='relu'))
	model.add(Flatten())
	model.add(Dense(2, activation='softmax'))
	model.compile(optimizer=opt, loss='binary_crossentropy', metrics=['accuracy']) 
	model.summary()
	# A	
	return model

def CNN_3(input_shape, num_filters, opt, lr):
	opt = opt_list[opt](lr=lr)
	model = Sequential(name="CNN_model_3")
	model.add(Conv2D(filters=16, kernel_size=2, strides=1, input_shape=input_shape, activation='relu'))
	model.add(Conv2D(filters=8, kernel_size=2, strides=1, input_shape=input_shape, activation='relu'))
	model.add(Flatten())
	model.add(Dense(2, activation='softmax'))
	model.compile(optimizer=opt, loss='binary_crossentropy', metrics=['accuracy']) 
	model.summary()
	# A	
	return model



__all__ = [
	"LR",
	"CNN_1",
	"CNN_2",
	"CNN_3"
]
