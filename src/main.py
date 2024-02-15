import os
import numpy as np
import json
import joblib
from datetime import datetime
from fastapi import FastAPI, HTTPException

# FastAPI caching and Redis backend for cache storage
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

# Async Redis client
from redis import asyncio as aioredis
from pydantic import BaseModel, Extra
from typing import List

# Initialize FastAPI application
app = FastAPI()

# Load the machine learning model for housing price prediction from a file
model = joblib.load("model_pipeline.pkl")

# Configuration for Redis cache storage
REDIS_HOST = "redis://redis"

# Caching function, used as a decorator to cache the results of API endpoints
@cache()
async def get_cache():
    return 1

# FastAPI event hook for application startup
@app.on_event("startup")
async def startup():
    # Initialize Redis client with the specified host, enabling UTF-8 encoding and response decoding
    redis = aioredis.from_url(REDIS_HOST, encoding="utf8", decode_responses=True)
    # Initialize FastAPI cache with Redis backend and a specific cache prefix
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

# Define a simple endpoint to return a greeting message
@app.get("/hello")
def read_hello(name: str):
    return {"message": f"hello {name}"}

# Define a root endpoint that immediately raises an HTTPException indicating the method is not supported
@app.get("/")
def root():
    raise HTTPException(
        status_code=501, detail="The request method is not supported."
    )

# Health check endpoint, returns the current server time in ISO format
@app.get("/health")
def health_check():
    current_time = datetime.now().isoformat()
    return {"time": f"{current_time}"}

# Pydantic model for housing data input, using strict field validation and forbidding extra fields
class House(BaseModel, extra=Extra.forbid):
    "Data model to parse the request body JSON."
    
    # Fields representing features of the house
    MedInc: float
    HouseAge: float
    AveRooms: float
    AveBedrms: float
    Population: float
    AveOccup: float
    Latitude: float
    Longitude: float

    # Convert model instance into a NumPy array for model prediction
    def to_np(self):
        return np.array(list(vars(self).values())).reshape(1, 8)

# Model for handling multiple housing data inputs
class Houses(BaseModel):
    houses: List[House]

# Response model specifying the structure of the prediction output
class HousePredictions(BaseModel):
    predictions: list[float]

# Endpoint for performing housing price predictions, accepts and returns data formatted according to Pydantic models
@app.post("/predict", response_model=HousePredictions)
@cache()  # Apply caching to improve performance for repeated requests
async def predict(houses:Houses):
    # Convert the list of House models into a NumPy array suitable for the prediction model
    model_inputs = np.array([list(house_dict.values()) for house_dict in houses.dict()['houses']])
    # Perform prediction using the loaded ML model
    model_results = model.predict(model_inputs)
    # Return the predictions in the specified response format
    return {"predictions": list(model_results)}
