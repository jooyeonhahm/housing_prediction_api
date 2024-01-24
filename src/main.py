import os
import numpy as np
import json
import joblib
from datetime import datetime
from fastapi import FastAPI, HTTPException

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

from redis import asyncio as aioredis
from pydantic import BaseModel, Extra
from typing import List

# FastAPI app
app = FastAPI()

# ML model for housing price prediction
model = joblib.load("model_pipeline.pkl")

# Redis Variable
REDIS_HOST = "redis://redis"

@cache()
async def get_cache():
    return 1

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url(REDIS_HOST, encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

# hello endpoint
@app.get("/hello")
def read_hello(name: str):
    return {"message": f"hello {name}"}

# root (not implemented)
@app.get("/")
def root():
    raise HTTPException(
        status_code=501, detail="The request method is not supported."
    )

# health endpoint returning the current time in the ISO format
@app.get("/health")
def health_check():
    current_time = datetime.now()
    current_time = current_time.isoformat()
    return {"time": f"{current_time}"}

# Pydantic request model for data input
class House(BaseModel, extra=Extra.forbid):
    "Data model to parse the request body JSON."
    
    MedInc: float
    HouseAge: float
    AveRooms: float
    AveBedrms: float
    Population: float
    AveOccup: float
    Latitude: float
    Longitude: float

    def to_np(self):
        return np.array(list(vars(self).values())).reshape(1, 8)

# Pydantic request model for list data input
class Houses(BaseModel):
    houses: List[House]

# Pydantic response model for output
class HousePredictions(BaseModel):
    predictions: list[float]

# Prediction end point that request and respond with pydantic models
@app.post("/predict", response_model=HousePredictions)
@cache()
async def predict(houses:Houses):
    model_inputs = np.array([list(house_dict.values()) for house_dict in houses.dict()['houses']])
    model_results = model.predict(model_inputs)
    return {"predictions": list(model_results)}
