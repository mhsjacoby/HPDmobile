'''
https://towardsdatascience.com/pca-using-python-scikit-learn-e653f8989e60
'''
import warnings
warnings.filterwarnings("ignore")

import os
import numpy as np
import matplotlib.pyplot as plt

import pickle


from utils import *
from models import *
from load_data import load_data
model_list = {"LR":LR, "CNN_1":CNN_1, "CNN_2":CNN_2, "CNN_3":CNN_3}


GPU_num = 1

import tensorflow as tf
os.environ['TF_CPP_MIN_LOG_LEVEL']='3'
os.environ["CUDA_VISIBLE_DEVICES"] = "1"
gpus = tf.config.experimental.list_physical_devices('GPU')
# print(gpus)

if gpus:
	# Restrict TensorFlow to only use the selected GPU
	try:
		tf.config.experimental.set_memory_growth(gpus[0], True)

		# tf.config.experimental.set_visible_devices(gpus[GPU_num], 'GPU')
		# tf.config.experimental.set_memory_growth(gpus[GPU_num], True)

		# logical_gpus = tf.config.experimental.list_logical_devices('GPU')
		# print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPU")
	except RuntimeError as e:
		# Visible devices must be set before GPUs have been initialized
		print(e)



houses = ["H1-red", "H2-red", "H3-red", "H4-red", "H5-red", "H6-black"]
# houses = ["H1-red"]
# houses = ["H2-red"]
# houses = ["H5-red"]


# model_name = "LR"
# model_name = "CNN_3"

database_choice = "train_test"


scaling = "filter"
# scaling = "sample"
# scaling = "minmax"



# CNN_1 params
model_name = "CNN_1"
opt = "sgd"
batch_size = 8
nb_epoch = 25
learning_rate = 3e-4
val_split_ratio = 0.2


# CNN_2 params
# model_name = "CNN_2"
# opt = "adam"
# batch_size = 8
# nb_epoch = 25
# learning_rate = 3e-4
# val_split_ratio = 0.2




# save_path = "resu/model_name_d6c4_opt_bs8_ep25_lr_val"

run_num = 3
save_path = f"{model_name}-{houses}/run_{run_num}"

if not os.path.exists(save_path):
	os.makedirs(save_path)

X_train, Y_train, X_test, Y_test = load_data(houses=houses, database_choice="train_test",scaling=scaling)
A
# ==== Scaling Input ====

num_filters = X_test.shape[1]
ori_X_shape = X_train.shape


# ==== Build model ====
if model_name == "LR":
	model = LR(input_dim=X_train.shape[1], opt=opt, lr=learning_rate)

elif model_name in ["CNN_1","CNN_2","CNN_3"]:
	# Reshape back to 3D, and with channel last by default
	X_train = X_train.reshape((len(X_train),ori_X_shape[1],ori_X_shape[2],1))
	X_test = X_test.reshape((len(X_test),ori_X_shape[1],ori_X_shape[2],1))	
	input_dim = (X_train.shape[1],X_train.shape[2],1)

	model = model_list[model_name](input_dim, num_filters, opt=opt, lr=learning_rate)


history = model.fit(X_train, Y_train, batch_size=batch_size, epochs=nb_epoch,verbose=1, validation_split=val_split_ratio) 

# Plot Accuracies
plt.figure()
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Model Accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Training Accuracies', 'Validation Accuracies'], loc='upper left')
plt.savefig(save_path+"/Model_acc.png")

# Plot losses
plt.figure()
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model Loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Training Loss', 'Validation Loss'], loc='upper left')
plt.savefig(save_path+"/Model_loss.png")


eval_model(model, X_test, Y_test)




# ================ Cross test ================
houses = ["H1-red", "H2-red", "H3-red", "H4-red", "H5-red", "H6-black"]
cross_test(model, houses, database_choice, scaling=scaling)

# A

# ================ Saving Model ================

# save model as json and yaml
print("Saving Model Architecture....")
json_string = model.to_json()
open(save_path+f'/{model_name}_model.json', 'w').write(json_string)

# save the weights in h5 format
print("Saving Model Weights....")
model.save_weights(save_path+f'/{model_name}_weights.h5')


