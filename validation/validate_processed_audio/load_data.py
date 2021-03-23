import numpy as np
import os
from utils import *

from sklearn.preprocessing import scale, MinMaxScaler
from tensorflow.keras.utils import to_categorical
import pickle


def load_data(houses, database_choice, scaling="filter"):
	for house in houses:
		npy_loc = os.path.join(house,database_choice)
		try: 
			x_train = np.vstack((x_train, np.load(npy_loc+"/X_train.npy"))) # (N, 16, 1000)
			y_train = np.hstack((y_train, np.load(npy_loc+"/Y_train.npy")))
			x_test  = np.vstack((x_test, np.load(npy_loc+"/X_test.npy")))
			y_test  = np.hstack((y_test, np.load(npy_loc+"/Y_test.npy")))
		except:
			x_train = np.load(npy_loc+"/X_train.npy")
			y_train = np.load(npy_loc+"/Y_train.npy")
			x_test  = np.load(npy_loc+"/X_test.npy")
			y_test  = np.load(npy_loc+"/Y_test.npy")


	# 	print(f"==== {house} ====")
	# 	print(f"y_train: {np.shape(y_train)}")
	# 	print(f"y_train sum: {np.sum(y_train)}")
	# 	print(f"y_train occ rate: {np.sum(y_train)/len(y_train)}\n")

	# 	print(f"y_test: {np.shape(y_test)}")
	# 	print(f"y_test sum: {np.sum(y_test)}")
	# 	print(f"y_test occ rate: {np.sum(y_test)/len(y_test)}\n")


	# A

	# Shuffle the x and y content IN THE SAME WAY
	x_train, y_train = shuffle_data(x_train, y_train)
	x_test, y_test   = shuffle_data(x_test, y_test)

	# ==== Scaling Input ====
	if scaling == "filter":
		x_train = norm_by_filter(x_train) # (2500, 16, 1000)
		x_test  = norm_by_filter(x_test)

	elif scaling == "sample":
		x_train = norm_by_sample(x_train)
		x_test  = norm_by_sample(x_test)

	elif scaling == "minmax":
		# Flatten for MinMaxScaler
		x_train = x_train.reshape((len(x_train),-1))
		x_test  = x_test.reshape((len(x_test),-1))

		scaler_x = MinMaxScaler(feature_range=(0, 1))
		x_train = scaler_x.fit_transform(x_train)
		x_test  = scaler_x.transform(x_test)
		# save the scaler
		pickle.dump(scaler_x, open('scaler.pkl', 'wb'))


	# One-hot Encode Output
	nb_classes = len(np.unique(y_test))
	y_train = to_categorical(y_train, nb_classes)
	y_test = to_categorical(y_test, nb_classes)

	print("==== Data dimension ====")
	print(f"x_train: {np.shape(x_train)}")
	print(f"y_train: {np.shape(y_train)}")
	print(f"x_test: {np.shape(x_test)}")
	print(f"y_test: {np.shape(y_test)}\n")

	return x_train, y_train, x_test, y_test



def shuffle_data(x,y):
	shuffle_idx = np.arange(x.shape[0])
	np.random.shuffle(shuffle_idx)
	shuffled_x  = x[shuffle_idx]
	shuffled_y  = y[shuffle_idx]
	return shuffled_x, shuffled_y



def load_wav_data(houses, scaling="filter"):

	for house in houses:
		npy_loc = os.path.join(house,"wav_train_test")
		try: 
			x_train = np.vstack((x_train, np.load(npy_loc+"/X_train.npy"))) # (N, 16, 1000)
			y_train = np.hstack((y_train, np.load(npy_loc+"/Y_train.npy")))
			x_test  = np.vstack((x_test, np.load(npy_loc+"/X_test.npy")))
			y_test  = np.hstack((y_test, np.load(npy_loc+"/Y_test.npy")))
		except:
			x_train = np.load(npy_loc+"/X_train.npy")
			y_train = np.load(npy_loc+"/Y_train.npy")
			x_test  = np.load(npy_loc+"/X_test.npy")
			y_test  = np.load(npy_loc+"/Y_test.npy")

	# Shuffle the x and y content IN THE SAME WAY
	x_train, y_train = shuffle_data(x_train, y_train)
	x_test, y_test   = shuffle_data(x_test, y_test)

	print("==== Data dimension ====")
	print(f"x_train: {np.shape(x_train)}")
	print(f"y_train: {np.shape(y_train)}")
	print(f"x_test: {np.shape(x_test)}")
	print(f"y_test: {np.shape(y_test)}\n")


	# # ==== Scaling Input ====
	if scaling == "filter":
		x_train = norm_by_filter(x_train) # (2500, 16, 1000)
		x_test  = norm_by_filter(x_test)

	elif scaling == "sample":
		x_train = norm_by_sample(x_train)
		x_test  = norm_by_sample(x_test)

	elif scaling == "minmax":
		# Flatten for MinMaxScaler
		x_train = x_train.reshape((len(x_train),-1))
		x_test  = x_test.reshape((len(x_test),-1))

		scaler_x = MinMaxScaler(feature_range=(0, 1))
		x_train = scaler_x.fit_transform(x_train)
		x_test  = scaler_x.transform(x_test)
		# save the scaler
		pickle.dump(scaler_x, open('wav_scaler.pkl', 'wb'))


	# One-hot Encode Output
	nb_classes = len(np.unique(y_test))
	y_train = to_categorical(y_train, nb_classes)
	y_test = to_categorical(y_test, nb_classes)

	return x_train, y_train, x_test, y_test
