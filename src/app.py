import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import os

# Создаем экземпляр FastAPI
app = FastAPI()

# Загружаем модель
exp_path = os.path.join(os.getcwd(), "experiments")
model_path = os.path.join(exp_path, "log_reg.sav")
model = joblib.load(model_path)


# Определяем класс Pydantic модели для входных данных
class InputData(BaseModel):
    X: list
    y: list


# Определяем эндпоинт для предсказаний
@app.post("/predict/")
async def predict(input_data: InputData):
    try:
        # Преобразуем данные в DataFrame
        df = pd.DataFrame(input_data.X, columns=[str(i) for i in range(len(input_data.X[0]))])

        # Выполняем предсказание
        predictions = model.predict(df)

        # Формируем ответ
        response = {"predictions": predictions.tolist()}
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html


@app.get("/docs", response_class=HTMLResponse)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="API docs")


@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint():
    return JSONResponse(get_openapi(title="Your Project Name", version="0.1.0", routes=app.routes))
