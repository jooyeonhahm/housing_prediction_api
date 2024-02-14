# Import required libraries
from datetime import datetime
import joblib
import numpy as np

# Record the start time of the model loading process
start = datetime.now()
# Load the trained model from a file
model = joblib.load("model_pipeline.pkl")
# Record the end time of the model loading process
end = datetime.now()
# Print the time taken to load the model
print(f"time to load model: {end-start}")

# Define a sample input array for making predictions
# This array mimics the structure of the input data the model expects
x = np.array(
    [
        [8.3252, 41.0, 6.98412698, 1.02380952, 322.0, 2.55555556, 37.88, -122.23],
        [8.3252, 41.0, 6.98412698, 1.02380952, 322.0, 2.55555556, 37.88, -122.23],
        [8.3252, 41.0, 6.98412698, 1.02380952, 322.0, 2.55555556, 37.88, -122.23],
        [8.3252, 41.0, 6.98412698, 1.02380952, 322.0, 2.55555556, 37.88, -122.23],
        [8.3252, 41.0, 6.98412698, 1.02380952, 322.0, 2.55555556, 37.88, -122.23],
    ]
)

# Print the shape of the input data
print(f"shape of input data: {x.shape}") 

# Perform vectorized predictions
start = datetime.now()  # Start timing the vectorized predictions
predictions_vectorized = model.predict(x)  # Predict using the model
end = datetime.now()  # End timing the vectorized predictions
print(f"time to perform vectorized predictions: {end - start}")  # Print the time taken for vectorized predictions
print(f"Vectorized predictions: {predictions_vectorized}")  # Print the vectorized predictions

# Perform for-loop iterated predictions
start = datetime.now()  # Start timing the for-loop iterated predictions
predictions_iterated = [model.predict(item.reshape(-1, 8)) for item in x]  # Predict using a for-loop
end = datetime.now()  # End timing the for-loop iterated predictions
print(f"time to perform for-loop iterated predictions: {end - start}")  # Print the time taken for for-loop iterated predictions
print(f"For-loop iterated predictions: {predictions_iterated}")  # Print the iterated predictions

# target: 4.526