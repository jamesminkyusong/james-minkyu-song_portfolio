import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report, accuracy_score
import matplotlib.pyplot as plt
import asl_classifier.util as util

# Load data
train_df = pd.read_csv(util.get_path("data", "final_train.csv"))
test_df = pd.read_csv(util.get_path("data", "final_test.csv"))

# Preprocessing steps
# Extract features and target from the train and test data
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report, accuracy_score

# Preprocessing steps
train_df = train_df.drop(train_df.filter(regex='^label_').columns, axis=1)
test_df = test_df.drop(test_df.filter(regex='^label_').columns, axis=1)
X_train = train_df.drop(['label', 'type'], axis=1)
y_train = train_df['label']
X_test= test_df.drop(['label', 'type'], axis=1)
y_test = test_df['label']
y_test = test_df['label']

# Random Forest Model
rf_model = RandomForestClassifier(n_estimators=400, min_samples_split= 2, min_samples_leaf=1, max_features= 'auto', max_depth= 40, random_state=42)
rf_model.fit(X_train, y_train)
y_pred = rf_model.predict(X_test)

# Evaluation
accuracy = accuracy_score(y_test, y_pred)
classification_rep = classification_report(y_test, y_pred)
print("Accuracy:", accuracy)
print("\nClassification Report:\n", classification_rep)

# Hyperparameter Tuning using GridSearchCV
param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [None, 10, 20, 30],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
    'max_features': ['auto', 'sqrt']
}
grid_search = GridSearchCV(estimator=rf_model, param_grid=param_grid, cv=3, n_jobs=-1, verbose=2, scoring='accuracy')
grid_search.fit(X_train, y_train)

# Best Model Evaluation
best_params = grid_search.best_params_
best_model = grid_search.best_estimator_
best_y_pred = best_model.predict(X_test)
best_accuracy = accuracy_score(y_test, best_y_pred)
best_classification_report = classification_report(y_test, best_y_pred)

print("Best Model Parameters:", best_params)
print("Best Model Accuracy:", best_accuracy)
print("\nBest Model Classification Report:\n", best_classification_report)
