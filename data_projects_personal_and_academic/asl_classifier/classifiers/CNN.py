import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import asl_classifier.util as util


# Load data
train_df = pd.read_csv(util.get_path("data", "final_train.csv"))
test_df = pd.read_csv(util.get_path("data", "final_test.csv"))

# Preprocessing and normalization
X_train = train_df.drop(columns=["type", "label"] + [f"label_{i}" for i in range(25) if i != 9]).values
y_train = train_df[train_df.columns[786:]].values
X_test = test_df.drop(columns=["type", "label"] + [f"label_{i}" for i in range(25) if i != 9]).values
y_test = test_df[test_df.columns[786:]].values

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)


# Reshape for CNN input
X_train2 = X_train.reshape(-1, 28, 28, 1)
X_test2 = X_test.reshape(-1, 28, 28, 1)

# CNN Model
model = Sequential()
model.add(Conv2D(filters=32, kernel_size=(3, 3), activation='relu', input_shape=X_train2.shape[1:]))
model.add(MaxPooling2D(pool_size=(2, 2)))
# Add more layers as needed
model.add(Flatten())
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(np.unique(y_train)), activation='softmax'))  # Assuming y_train is already encoded

# Compile the model
model.compile(loss='categorical_crossentropy', optimizer=Adam(learning_rate=0.001), metrics=['accuracy'])

# Train the model
history = model.fit(X_train2, y_train, epochs=20, batch_size=32, validation_split=0.2)

# Evaluate the model
loss, accuracy = model.evaluate(X_test2, y_test)
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

preds = model.predict(X_test2)

y_pred_labels = np.argmax(preds, axis=1)
y_true_labels = np.argmax(y_test, axis=1)

y_pred_labels_adjusted = adjust_labels(y_pred_labels)
y_true_labels_adjusted = adjust_labels(y_true_labels)

class_report = classification_report(y_true_labels_adjusted, y_pred_labels_adjusted)
print("Classification Report:\n", class_report)