from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import numpy as np
from copy import deepcopy
import os

def eval_model(model, X_test, Y_test, save_path, verbose=1):

	# Evaluate Model
	# score = model.evaluate(X_test, Y_test, verbose=0)
	# print('Test score:', score[0]) 
	# print('Test accuracy:', score[1])

	Y_pred = (model.predict(X_test)>0.5).astype("int32")
	y_pred = np.argmax(Y_pred, axis=1)
	y_test = np.argmax(Y_test, axis=1)
	print('Accuracy Score:')
	acc = accuracy_score(y_test, y_pred)
	print(acc)

	if verbose >= 1:
		print('Confusion Matrix:')
		cm = confusion_matrix(y_test, y_pred)
		print(cm)
		return acc, cm

	if verbose >= 2:
		print('Classification Report:')
		target_names = ['Quiet', 'Noisy']
		print(classification_report(y_test, y_pred, target_names=target_names))
		return acc, cm

	return acc, None


def norm_by_filter(data):
	# Assume data dimension: (N，16，1000)
	N,num_filter,filter_data_len = data.shape
	assert filter_data_len>num_filter, "Assume data dimension: (N_samples, num_filter, filter_data_len)"

	scaled_data = deepcopy(data)
	for N in range(len(data)):
		for filter_ in range(len(data[N])): # (0, 0, 1000)
			scaled_data[N][filter_] = (scaled_data[N][filter_]-np.min(scaled_data[N][filter_]))/(np.max(scaled_data[N][filter_])-np.min(scaled_data[N][filter_]))
	return scaled_data


def norm_by_sample(data):
	# Assume data dimension: (N，16，1000)
	N,num_filter,filter_data_len = data.shape
	assert filter_data_len>num_filter, "Assume data dimension: (N_samples, num_filter, filter_data_len)"
	
	scaled_data = deepcopy(data)
	for N in range(len(data)):
		scaled_data[N] = (scaled_data[N]-np.min(scaled_data[N]))/(np.max(scaled_data[N])-np.min(scaled_data[N]))
	return scaled_data


def cross_test(model, houses, database_choice, save_path, scaling="filter"):
	from load_data import load_data
	acc_log = []
	cm_log = []
	for house in houses:
		print(f"================ Cross testing with {house} Test data ================")
		_, _, X_test_cross, Y_test_cross = load_data(houses=[house],database_choice=database_choice,scaling=scaling)

		# Combine train test data
		# X = np.vstack((X_train,X_test))

		# Prepare Labels
		# y = np.hstack((y_train,y_test))

		# Scaling Input - try scaling with own scaler later
		# X_test_cross = scaler_x.transform(X)


		ori_X_shape  = X_test_cross.shape
		X_test_cross = X_test_cross.reshape((len(X_test_cross),ori_X_shape[1],ori_X_shape[2],1))

		acc, cm = eval_model(model, X_test_cross, Y_test_cross, save_path)

		acc_log.append(acc)
		cm_log.append((cm.ravel()))

	np.savetxt(os.path.join(save_path,"acc.csv"), acc_log, delimiter = ",",fmt='%.18f')
	np.savetxt(os.path.join(save_path,"cm.csv"), cm_log, delimiter = ",",fmt='%i')


__all__ = [
	"eval_model",
	"norm_by_filter",
	"norm_by_sample",
	"cross_test",
]
