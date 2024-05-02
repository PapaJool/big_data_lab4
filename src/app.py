import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import os



import sys

# Добавляем текущий каталог в PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Database class
import db_init
from kafka_service import KafkaService

# Создаем экземпляр FastAPI
app = FastAPI()

# Load model
exp_path = os.path.join(os.getcwd(), "experiments")
model_path = os.path.join(exp_path, "log_reg.sav")
model = joblib.load(model_path)

# Initialize the database
db = db_init.Database()
db.create_database("lab2_bd")
db.create_table("predictions", {'X': 'Array(Float64)', 'y': 'Int32', 'predictions': 'Int32'})

kafka_service = KafkaService()
# Define the Pydantic input data model
class InputData(BaseModel):
    X: list
    y: list

# Define the endpoint for predictions
@app.post("/predict/")
async def predict(input_data: InputData):
    try:
        # Преобразуем данные X в одномерный массив
        X_db = list(input_data.X[0].values())
        X = [list(sample.values()) for sample in input_data.X]
        y = input_data.y[0]['0']

        predictions = model.predict(X)

        db.insert_data("predictions", X_db, int(y), int(predictions[0]))

        response = {
            'X': input_data.X,
            'y': input_data.y,
            'predictions': str(predictions[0])
        }

        kafka_service.send(response)


        response = {"predictions": predictions.tolist()}
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/check_predictions/")
def check_predictions():
    try:
        # Читаем данные из таблицы "predictions"
        data = db.read_table("predictions")
        data_json = data.to_json(orient="records")

        return data_json

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/clear_table/")
def clear_table():
    try:
        db.delete_data("predictions")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Swagger UI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html

@app.get("/docs", response_class=HTMLResponse)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="API docs")

@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint():
    return JSONResponse(get_openapi(title="Your Project Name", version="0.1.0", routes=app.routes))