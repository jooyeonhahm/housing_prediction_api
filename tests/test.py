from fastapi.testclient import TestClient
from src import __version__
from src.main import app
from datetime import datetime

client = TestClient(app)

def test_version():
    assert __version__ == "0.1.0"

def test_root():
    response = client.get("/")
    assert response.status_code == 501

def test_hello_no_param():
    response = client.get("/hello")
    assert response.status_code == 422

def test_hello_name():
    response = client.get("/hello?name=jooyeon")
    assert response.status_code == 200
    assert response.json() == {"message": "hello jooyeon"}

def test_docs():
    response = client.get("/docs")
    assert response.headers['content-type'] == 'text/html; charset=utf-8'
    assert response.status_code == 200

def test_json():
    response = client.get("/openapi.json")
    assert response.headers['content-type'] == 'application/json'
    assert response.status_code == 200

# health endpoint
def test_health():
    current_time = datetime.now()
    current_time = current_time.isoformat()
    current_time = current_time.split(".")[0]
    response = client.get("/health")
    mod_time_str = response.json()["time"]
    mod_time_str = mod_time_str.split(".")[0]
    assert response.status_code == 200
    assert current_time == mod_time_str

# predict endpoint tests
def test_predict():
    response = client.post("/predict")
    assert response.status_code == 422

# predict endpoint with a single input
def test_predict_basic():
    data = {
        "houses": [
            {
                "MedInc": 1,
                "HouseAge": 1,
                "AveRooms": 3,
                "AveBedrms": 3,
                "Population": 3,
                "AveOccup": 5,
                "Latitude": 1,
                "Longitude": 1,
            }
        ]
    }
    response = client.post(
        "/predict",
        json=data,
    )
    assert response.status_code == 200
    assert type(response.json()["predictions"]) is list

# predict endpoint with a list of inputs
def test_predict_list():
    list_data = {
        "houses": [
            {
                "MedInc": 1,
                "HouseAge": 1,
                "AveRooms": 3,
                "AveBedrms": 3,
                "Population": 3,
                "AveOccup": 5,
                "Latitude": 1,
                "Longitude": 1,
            },
            {
                "MedInc": 9.5,
                "HouseAge": 42.1,
                "AveRooms": 7.01,
                "AveBedrms": 1.50,
                "Population": 315,
                "AveOccup": 2.5,
                "Latitude": 38.1,
                "Longitude": -121.1,
            }
        ]
    }
    response = client.post(
        "/predict",
        json=list_data,
    )
    assert response.status_code == 200
    assert type(response.json()["predictions"]) is list

# Test predict endpoint with invalid input(extra feature)
def test_predict_extra_feature():
    data = {
        "houses": [
            {
                "MedInc": 1,
                "HouseAge": 1,
                "AveRooms": 3,
                "AveBedrms": 3,
                "Population": 3,
                "AveOccup": 5,
                "Latitude": 1,
                "Longitude": 1,
                "ExtraFeature": -1,
            }
        ]
    }
    response = client.post(
        "/predict",
        json=data,
    )
    assert response.status_code == 422


# Test predict endpoint with invalid input(missing values)
def test_predict_missing_feature():
    data = {
        "houses": [
            {
                "MedInc": 1,
                "HouseAge": 1,
                "AveRooms": 3,
                "AveBedrms": 3,
                "Population": 3,
                "AveOccup": 5,
                "Latitude": 1,
            }
        ]
    }
    response = client.post(
        "/predict",
        json=data,
    )
    assert response.status_code == 422
