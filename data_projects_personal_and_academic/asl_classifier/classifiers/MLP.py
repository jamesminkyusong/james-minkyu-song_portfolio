import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt
import asl_classifier.util as util

# Load data
train_df = pd.read_csv(util.get_path("data", "final_train.csv"))
test_df = pd.read_csv(util.get_path("data", "final_test.csv"))

# Preprocessing and normalization
X_train = train_df.drop(columns=["type", "label"] + [f"label_{i}" for i in range(25) if i != 9])
y_train = train_df[train_df.columns[786:]]
X_test = test_df.drop(columns=["type", "label"] + [f"label_{i}" for i in range(25) if i != 9])
y_test = test_df[test_df.columns[786:]]

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)


# MLP Model
model = Sequential()
model.add(Dense(256, activation='relu', input_shape=(X_train.shape[1],)))
model.add(Dropout(0.2))
model.add(Dense(128, activation='relu'))
model.add(Dense(64, activation='relu'))
model.add(Dense(y_train.shape[1], activation='softmax'))  # Output layer

# Compile the model
optimizer = Adam(learning_rate=0.001)
model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])

# Train the model
history = model.fit(X_train, y_train, epochs=50, batch_size=64, validation_split=0.2)


# Evaluate the model
loss, accuracy = model.evaluate(X_test, y_test)
print(f"Test Accuracy: {accuracy}")

# Visualization of training results
epochs = range(1, len(history.history['accuracy']) + 1)
plt.figure(figsize=(16, 9))

# Accuracy plot
plt.subplot(1, 2, 1)
plt.plot(epochs, history.history['accuracy'], 'go-', label='Training Accuracy')
plt.plot(epochs, history.history['val_accuracy'], 'ro-', label='Validation Accuracy')
plt.title('Training & Validation Accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()

# Loss plot
plt.subplot(1, 2, 2)
plt.plot(epochs, history.history['loss'], 'g-o', label='Training Loss')
plt.plot(epochs, history.history['val_loss'], 'r-o', label='Validation Loss')
plt.title('Training & Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()

plt.show()

def adjust_labels(labels):
    adjusted_labels = []
    for label in labels:
        if label >= 9:
            adjusted_labels.append(label + 1)  # Adjust for missing 'J'
        else:
            adjusted_labels.append(label)
    return np.array(adjusted_labels)

preds = model.predict(X_test)

y_pred_labels = np.argmax(preds, axis=1)
y_true_labels = np.argmax(y_test.values, axis=1)

y_pred_labels_adjusted = adjust_labels(y_pred_labels)
y_true_labels_adjusted = adjust_labels(y_true_labels)


class_report = classification_report(y_true_labels_adjusted, y_pred_labels_adjusted)
print("Classification Report:\n", class_report)