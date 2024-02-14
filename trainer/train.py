# Import Statements
from os import getcwd
from os.path import exists, join

import joblib
from sklearn.datasets import fetch_california_housing
from sklearn.impute import SimpleImputer  # Imputer for missing values
from sklearn.model_selection import GridSearchCV, train_test_split  # GridSearchCV for hyperparameter tuning and function for splitting dataset
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import RobustScaler
from sklearn.svm import SVR

# Fetch the California housing dataset
data = fetch_california_housing()

# Extract features and target variable from the dataset
features = data.feature_names  # Get names of the features
X = data.data  # Feature matrix
y = data.target  # Target variable (housing prices)

# Print the feature names and first five examples from the dataset
print(f"features: {features}")
for i in range(5):
    print(f"Example {i}:\n {X[i]}, {y[i]}")

# Split the dataset into training and test sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.33, random_state=42
)

# Define a preprocessing and modeling pipeline
processing_pipeline = make_pipeline(
    SimpleImputer(),  # Impute missing values
    RobustScaler(),  # Scale features using robust scaler
    SVR()  # Support Vector Regressor
)

# Set up hyperparameters for grid search
params = {
    "simpleimputer__strategy": ["mean", "median"],  # Strategies for imputation
    "robustscaler__quantile_range": [(25.0, 75.0), (30.0, 70.0)],  # Quantile range for robust scaler
    "svr__C": [0.1, 1.0],  # Penalty parameter C for SVR
    "svr__gamma": ["auto", 0.1],  # Kernel coefficient for SVR
}

# Initialize GridSearchCV to find the best hyperparameters using cross-validation
grid = GridSearchCV(processing_pipeline, param_grid=params, n_jobs=-1, cv=5, verbose=3)

# Define the filename and path to save the trained model
model_filename = "model_pipeline.pkl"
model_path = join(getcwd(), model_filename)
print(model_path)

# Check if the model has already been trained and saved
if not exists(model_path):
    # If not, fit the model on the training data
    grid.fit(X_train, y_train)

    # Print performance metrics and best parameters
    print(f"Train R^2 Score : {grid.best_estimator_.score(X_train, y_train):.3f}")
    print(f"Test R^2 Score : {grid.best_estimator_.score(X_test, y_test):.3f}")
    print(f"Best R^2 Score Through Grid Search : {grid.best_score_:.3f}")
    print(f"Best Parameters : {grid.best_params_}")

    # Save the best model from grid search
    joblib.dump(grid.best_estimator_, model_path)
else:
    # If model already exists, skip training
    print("Model has already been trained, no need to rerun")
