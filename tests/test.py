from fastapi.testclient import TestClient
from src import __version__  # Import the version of the application from src package.
from src.main import app
from datetime import datetime

client = TestClient(app)  # Initialize TestClient with the FastAPI app for testing.

def test_version():
    # Test to verify that the application version matches the expected version.
    assert __version__ == "0.1.0"

def test_root():
    # Test the root endpoint to ensure it returns a 501 status code (Not Implemented).
    response = client.get("/")
    assert response.status_code == 501

def test_hello_no_param():
    # Test the '/hello' endpoint without providing a 'name' query parameter to ensure it returns a 422 status code (Unprocessable Entity).
    response = client.get("/hello")
    assert response.status_code == 422

def test_hello_name():
    # Test the '/hello' endpoint with a 'name' query parameter and verify the response.
    response = client.get("/hello?name=jooyeon")
    assert response.status_code == 200
    assert response.json() == {"message": "hello jooyeon"}

def test_docs():
    # Test accessing the Swagger UI documentation at '/docs' and verify the content type and status code.
    response = client.get("/docs")
    assert response.headers['content-type'] == 'text/html; charset=utf-8'
    assert response.status_code == 200

def test_json():
    # Test accessing the OpenAPI schema at '/openapi.json' and verify the content type and status code.
    response = client.get("/openapi.json")
    assert response.headers['content-type'] == 'application/json'
    assert response.status_code == 200

def test_health():
    # Test the '/health' endpoint and compare the returned time with the current time to ensure the API is live.
    current_time = datetime.now().isoformat().split(".")[0]  # Current time without microseconds.
    response = client.get("/health")
    mod_time_str = response.json()["time"].split(".")[0]  # Time returned by the '/health' endpoint without microseconds.
    assert response.status_code == 200
    assert current_time == mod_time_str

def test_predict():
    # Test the '/predict' endpoint without providing required input data to ensure it returns a 422 status code.
    response = client.post("/predict")
    assert response.status_code == 422

def test_predict_basic():
    # Test the '/predict' endpoint with a single input to verify the predictions are returned as a list.
    data = {
        "houses": [
            {
                "MedInc": 1, "HouseAge": 1, "AveRooms": 3, "AveBedrms": 3, "Population": 3, "AveOccup": 5, "Latitude": 1, "Longitude": 1,
            }
        ]
    }
    response = client.post("/predict", json=data)
    assert response.status_code == 200
    assert type(response.json()["predictions"]) is list

def test_predict_list():
    # Test the '/predict' endpoint with a list of inputs to verify the predictions are returned as a list.
    list_data = {
        "houses": [
            # Provide two different sets of input data for prediction.
            {
                "MedInc": 1, "HouseAge": 1, "AveRooms": 3, "AveBedrms": 3, "Population": 3, "AveOccup": 5, "Latitude": 1, "Longitude": 1,
            },
            {
                "MedInc": 9.5, "HouseAge": 42.1, "AveRooms": 7.01, "AveBedrms": 1.50, "Population": 315, "AveOccup": 2.5, "Latitude": 38.1, "Longitude": -121.1,
            }
        ]
    }
    response = client.post("/predict", json=list_data)
    assert response.status_code == 200
    assert type(response.json()["predictions"]) is list

def test_predict_extra_feature():
    # Test the '/predict' endpoint with input data containing an extra, unexpected feature to ensure it returns a 422 status code.
    data = {
        "houses": [
            {
                "MedInc": 1, "HouseAge": 1, "AveRooms": 3, "AveBedrms": 3, "Population": 3, "AveOccup": 5, "Latitude": 1, "Longitude": 1, "ExtraFeature": -1,
            }
        ]
    }
    response = client.post
