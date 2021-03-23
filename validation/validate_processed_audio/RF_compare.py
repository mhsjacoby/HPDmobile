from load_data import load_data
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier

from joblib import dump
from platform import python_version
from struct import calcsize



houses = ["H1-red", "H2-red", "H3-red", "H4-red", "H5-red", "H6-black"]
# houses = ["H1-red"]
# houses = ["H2-red"]

scaling = "filter"
depth = 10

test_houses = ["H1-red", "H2-red", "H3-red", "H4-red", "H5-red", "H6-black"]

for _ in range(3):

	X_train, Y_train, _, _ = load_data(houses=houses, database_choice="train_test",scaling=scaling)

	X_train = X_train.reshape((len(X_train),-1))

	clf = RandomForestClassifier(max_depth=depth, random_state=0)
	clf.fit(X_train, Y_train)

	# y_pred = clf.predict(X_test)
	# acc = accuracy_score(Y_test, y_pred)
	# print(acc)



	for th in test_houses:
		print(f"Cross test with {th}")
		_, _, X_test, Y_test = load_data(houses=[th], database_choice="train_test",scaling=scaling)
		X_test  = X_test.reshape((len(X_test),-1))

		y_pred = clf.predict(X_test)
		acc = accuracy_score(Y_test, y_pred)
		print(acc)		

	# print("Cross test with H1-red")
	# _, _, X_test, Y_test = load_data(houses=["H1-red"],scaling=scaling)
	# X_test  = X_test.reshape((len(X_test),-1))

	# y_pred = clf.predict(X_test)
	# acc = accuracy_score(Y_test, y_pred)
	# print(acc)


	# print("Cross test with H2-red")
	# _, _, X_test, Y_test = load_data(houses=["H2-red"],scaling=scaling)
	# X_test  = X_test.reshape((len(X_test),-1))

	# y_pred = clf.predict(X_test)
	# acc = accuracy_score(Y_test, y_pred)
	# print(acc)


# Save model
# dump(clf, "trained_RF(%s-%s).joblib"%(python_version(),calcsize("P")*8)) # Model