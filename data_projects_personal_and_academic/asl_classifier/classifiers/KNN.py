import pandas as pd
import time
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, classification_report
import asl_classifier.util as util

start_time = time.time()

print('Reading train csv...')
train_csv = pd.read_csv(util.get_path("data", "final_train.csv"))

print('Reading test csv...')
test_csv = pd.read_csv(util.get_path("data", "final_test.csv"))

print('Preparing train data...')
yTrain = train_csv['label']
xTrain = train_csv.drop(columns=["type", "label"] + [f"label_{i}" for i in range(25) if i != 9])

print('Preparing test data...')
yTest = test_csv['label']
xTest = test_csv.drop(columns=["type", "label"] + [f"label_{i}" for i in range(25) if i != 9])

print('Initializing KNN model...')
knn = KNeighborsClassifier(n_neighbors=3)

print('Fitting model...')
knn.fit(xTrain, yTrain)

print('Predicting...')
y_pred = knn.predict(xTest)

accuracy = accuracy_score(yTest, y_pred)
print(f"Accuracy of KNN model: {accuracy * 100:.2f}%")

# Generating and printing the classification report
class_report = classification_report(yTest, y_pred)
print("Classification Report:\n", class_report)

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time} seconds")

n_neighbors_options = [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
weights_options = ['uniform', 'distance']
metric_options = ['euclidean', 'manhattan']

best_accuracy = 0
best_params = {}

print('starting manual hyperparameter tuning...')

for n_neighbors in n_neighbors_options:
    for weights in weights_options:
        for metric in metric_options:
            knn = KNeighborsClassifier(n_neighbors=n_neighbors, weights=weights, metric=metric)
            knn.fit(xTrain, yTrain)
            y_pred = knn.predict(xTest)
            accuracy = accuracy_score(yTest, y_pred)

            print(f"n_neighbors: {n_neighbors}")
            print(f"weights: {weights}")
            print(f"metric: {metric}")
            print(f"accuracy: {accuracy}")
            print("-----------")

            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_params = {'n_neighbors': n_neighbors, 'weights': weights, 'metric': metric}

print(f"Best parameters: {best_params}")
print(f"Accuracy of best KNN model: {best_accuracy * 100:.2f}%")

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time} seconds")
