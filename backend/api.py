from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Set, Union, Tuple, Any
import json
import os
import time
import logging
import uuid
import uvicorn
import numpy as np
import io
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt
from PIL import Image
from contextlib import asynccontextmanager
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("api.log")
    ]
)
logger = logging.getLogger("young_diagrams_api")

# Импортируем наши классы симуляторов
from diagrams2d import DiagramSimulator2D
from diagrams3d import DiagramSimulator3D
from common.utils import save_cells_to_file

# Константы для настроек приложения
APP_NAME = "Young Diagrams API"
API_VERSION = "1.1.0"
DEBUG = False
ALLOWED_ORIGINS = ["*"]
PORT = 8000
HOST = "0.0.0.0"

# Менеджер жизненного цикла для инициализации и завершения ресурсов
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Код выполняется при запуске приложения
    logger.info(f"Запуск приложения {APP_NAME} v{API_VERSION}")
    yield  # Здесь приложение работает
    logger.info(f"Завершение работы приложения {APP_NAME}")

# FastAPI app
app = FastAPI(
    title=APP_NAME,
    description="API для симуляции и визуализации диаграмм Юнга",
    version=API_VERSION,
    lifespan=lifespan,
    debug=DEBUG
)

# Добавляем CORS middleware для обработки запросов с разных источников
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Middleware для логирования запросов
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware для логирования запросов и времени их выполнения.
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Добавляем request_id для отслеживания
    request.state.request_id = request_id
    logger.info(f"Начало запроса {request_id}: {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = request_id
        
        logger.info(f"Завершение запроса {request_id}: {response.status_code} за {process_time:.4f}с")
        return response
    except Exception as e:
        logger.error(f"Ошибка в запросе {request_id}: {str(e)}")
        raise
        
class SimulationParams2D(BaseModel):
    steps: int = Field(100, ge=10, le=10000, description="Количество шагов симуляции")
    alpha: float = Field(1.0, ge=-4.0, le=4.0, description="Параметр альфа для распределения")
    runs: int = Field(1, ge=1, le=100, description="Количество повторений для агрегирования данных")

class SimulationParams3D(BaseModel):
    steps: int = Field(100, ge=10, le=10000, description="Количество шагов симуляции")
    alpha: float = Field(1.0, ge=-4.0, le=4.0, description="Параметр альфа для распределения")
    runs: int = Field(1, ge=1, le=100, description="Количество повторений для агрегирования данных")

# Глобальные переменные для хранения результатов последних симуляций
last_2d_simulation = None
last_3d_simulation = None

# Функция для конвертации результатов симуляции в формат для API
def process_2d_cells(result):
    """
    Обрабатывает результаты 2D симуляции для API.
    """
    cells = []
    # Если результат имеет атрибут total_cell_counts (это экземпляр DiagramSimulator2D)
    if hasattr(result, 'total_cell_counts') and result.total_cell_counts:
        max_count = max(result.total_cell_counts.values())
        for (x, y), count in result.total_cell_counts.items():
            cells.append({
                "x": x,
                "y": y,
                "count": count,
                "normalized_count": count / max_count
            })
    # Если результат уже словарь с данными ячеек
    elif isinstance(result, dict) and "cells" in result:
        cells = result["cells"]
    
    if not cells:
        raise ValueError("Не удалось обработать данные ячеек")
    
    return cells

def process_3d_cells(result):
    """
    Обрабатывает результаты 3D симуляции для API.
    """
    cells = []
    # Если результат имеет атрибут total_cell_counts (это экземпляр DiagramSimulator3D)
    if hasattr(result, 'total_cell_counts') and result.total_cell_counts:
        max_count = max(result.total_cell_counts.values())
        for (x, y, z), count in result.total_cell_counts.items():
            cells.append({
                "x": x,
                "y": y,
                "z": z,
                "count": count,
                "normalized_count": count / max_count
            })
    # Если результат уже словарь с данными ячеек
    elif isinstance(result, dict) and "cells" in result:
        cells = result["cells"]
    
    if not cells:
        raise ValueError("Не удалось обработать данные ячеек")
    
    return cells

# Endpoint для проверки статуса API (health check)
@app.get("/", tags=["Статус"])
async def root():
    """Корневой endpoint API."""
    return {
        "message": "Добро пожаловать в API для моделирования диаграмм Юнга!",
        "version": API_VERSION,
        "status": "ok"
    }

# Более детальный endpoint для проверки статуса
@app.get("/status", tags=["Статус"])
async def check_status():
    """Проверка статуса API."""
    return {
        "status": "ok",
        "message": "API работает",
        "version": API_VERSION,
        "debug_mode": DEBUG
    }

# API для 2D диаграмм - сохраняем оригинальные URL пути
@app.post("/simulate/2d", tags=["2D Симуляции"])
async def simulate_2d(params: SimulationParams2D):
    """
    Запуск симуляции 2D диаграммы Юнга.
    
    Выполняет симуляцию и сохраняет результаты для последующей визуализации.
    """
    global last_2d_simulation
    
    try:
        logger.info(f"Starting 2D simulation with params: {params}")
        
        # Создаем экземпляр симулятора
        simulator = DiagramSimulator2D()
        
        # Запускаем симуляцию
        simulator.simulate(
            n_steps=params.steps,
            alpha=params.alpha,
            runs=params.runs
        )
        
        # Обрабатываем результаты симуляции
        cells = process_2d_cells(simulator)
        
        # Создаем результат для хранения
        result = {
            "cells": cells,
            "status": "success",
            "dimensions": {
                "max_x": max(x["x"] for x in cells) + 1 if cells else 0,
                "max_y": max(x["y"] for x in cells) + 1 if cells else 0
            },
            "metadata": {
                "steps": params.steps,
                "alpha": params.alpha,
                "runs": params.runs,
                "completed_at": datetime.now().isoformat()
            }
        }
        
        # Сохраняем результат в глобальную переменную
        last_2d_simulation = result
        
        # Подготавливаем результат для фронтенда
        frontend_cells = []
        for cell in cells:
            frontend_cells.append({
                "x": cell["x"],
                "y": cell["y"],
                "value": cell.get("normalized_count", 1.0)
            })
            
        logger.info(f"2D симуляция успешно завершена. Создано {len(cells)} клеток.")
        return {"cells": frontend_cells, "status": "success"}
    except Exception as e:
        logger.error(f"Ошибка при запуске симуляции 2D: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при симуляции: {str(e)}"
        )

@app.get("/visualize/2d", tags=["2D Симуляции"])
async def visualize_2d():
    """Визуализация последней 2D симуляции."""
    global last_2d_simulation
    
    if not last_2d_simulation:
        raise HTTPException(
            status_code=404,
            detail="Нет доступных данных симуляции. Запустите симуляцию сначала."
        )
    
    try:
        # Преобразуем ячейки в формат, который нужен фронтенду
        cells = []
        if "cells" in last_2d_simulation and isinstance(last_2d_simulation["cells"], list):
            for cell in last_2d_simulation["cells"]:
                if isinstance(cell, dict) and "x" in cell and "y" in cell:
                    cells.append({
                        "x": cell["x"],
                        "y": cell["y"],
                        "value": cell.get("normalized_count", 1.0)
                    })
        
        if not cells:
            raise ValueError("Ошибка при обработке данных ячеек")
            
        return {"cells": cells, "status": "success"}
    except Exception as e:
        logger.error(f"Ошибка в visualize_2d: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при визуализации: {str(e)}"
        )

@app.get("/limit-shape/2d", tags=["2D Симуляции"])
async def get_limit_shape_2d():
    """Получение предельной формы для 2D диаграммы."""
    global last_2d_simulation
    
    try:
        # Создаем симулятор
        simulator = DiagramSimulator2D()
        
        # Пытаемся использовать последнюю симуляцию, если доступна
        if last_2d_simulation and "cells" in last_2d_simulation:
            for cell in last_2d_simulation["cells"]:
                if "x" in cell and "y" in cell and "count" in cell:
                    simulator.total_cell_counts[(cell["x"], cell["y"])] = cell["count"]
        
        # Создаем визуализацию предельной формы
        fig = simulator.limit_shape_visualize()
        
        # Сохраняем изображение в формате base64
        buf = io.BytesIO()
        FigureCanvas(fig).print_png(buf)
        buf.seek(0)
        
        # Кодируем изображение в base64
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        
        return {"image": f"data:image/png;base64,{img_str}"}
    except Exception as e:
        logger.error(f"Ошибка при получении предельной формы 2D: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении предельной формы: {str(e)}"
        )

# API для 3D диаграмм - сохраняем оригинальные URL пути
@app.post("/simulate/3d", tags=["3D Симуляции"])
async def simulate_3d(params: SimulationParams3D):
    """
    Запуск симуляции 3D диаграммы Юнга.
    
    Выполняет симуляцию и сохраняет результаты для последующей визуализации.
    """
    global last_3d_simulation
    
    try:
        logger.info(f"Starting 3D simulation with params: {params}")
        
        # Создаем экземпляр симулятора
        simulator = DiagramSimulator3D()
        
        # Запускаем симуляцию
        simulator.simulate(
            n_steps=params.steps,
            alpha=params.alpha,
            runs=params.runs
        )
        
        # Обрабатываем результаты симуляции
        cells = process_3d_cells(simulator)
        
        # Создаем результат для хранения
        result = {
            "cells": cells,
            "status": "success",
            "dimensions": {
                "max_x": max(x["x"] for x in cells) + 1 if cells else 0,
                "max_y": max(x["y"] for x in cells) + 1 if cells else 0,
                "max_z": max(x["z"] for x in cells) + 1 if cells else 0
            },
            "metadata": {
                "steps": params.steps,
                "alpha": params.alpha,
                "runs": params.runs,
                "completed_at": datetime.now().isoformat()
            }
        }
        
        # Сохраняем результат в глобальную переменную
        last_3d_simulation = result
        
        # Подготавливаем результат для фронтенда
        frontend_cells = []
        for cell in cells:
            frontend_cells.append({
                "x": cell["x"],
                "y": cell["y"],
                "z": cell["z"],
                "value": cell.get("normalized_count", 1.0)
            })
            
        logger.info(f"3D симуляция успешно завершена. Создано {len(cells)} клеток.")
        return {"cells": frontend_cells, "status": "success"}
    except Exception as e:
        logger.error(f"Ошибка при запуске симуляции 3D: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при симуляции: {str(e)}"
        )

@app.get("/visualize/3d", tags=["3D Симуляции"])
async def visualize_3d():
    """
    Визуализация последней 3D симуляции.
    """
    global last_3d_simulation
    
    if not last_3d_simulation:
        raise HTTPException(
            status_code=404,
            detail="Нет доступных данных симуляции. Запустите симуляцию сначала."
        )
    
    try:
        # Преобразуем ячейки в формат, который нужен фронтенду
        cells = []
        if "cells" in last_3d_simulation and isinstance(last_3d_simulation["cells"], list):
            for cell in last_3d_simulation["cells"]:
                if isinstance(cell, dict) and "x" in cell and "y" in cell and "z" in cell:
                    cells.append({
                        "x": cell["x"],
                        "y": cell["y"],
                        "z": cell["z"],
                        "value": cell.get("normalized_count", 1.0)
                    })
                elif isinstance(cell, (list, tuple)) and len(cell) >= 3:
                    cells.append({
                        "x": cell[0],
                        "y": cell[1],
                        "z": cell[2],
                        "value": 1.0
                    })
        
        if not cells:
            raise ValueError("Ошибка при обработке данных ячеек")
            
        return {"cells": cells, "status": "success"}
    except Exception as e:
        logger.error(f"Ошибка в visualize_3d: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при визуализации: {str(e)}"
        )

@app.get("/limit-shape/3d", tags=["3D Симуляции"])
async def get_limit_shape_3d():
    """Получение предельной формы для 3D диаграммы."""
    global last_3d_simulation
    
    try:
        # Создаем симулятор
        simulator = DiagramSimulator3D()
        
        # Пытаемся использовать последнюю симуляцию, если доступна
        if last_3d_simulation and "cells" in last_3d_simulation:
            for cell in last_3d_simulation["cells"]:
                if "x" in cell and "y" in cell and "z" in cell and "count" in cell:
                    simulator.total_cell_counts[(cell["x"], cell["y"], cell["z"])] = cell["count"]
        
        # Создаем визуализацию предельной формы
        fig = simulator.visualize_limit_shape()
        
        # Сохраняем изображение в формате base64
        buf = io.BytesIO()
        FigureCanvas(fig).print_png(buf)
        buf.seek(0)
        
        # Кодируем изображение в base64
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        
        return {"image": f"data:image/png;base64,{img_str}"}
    except Exception as e:
        logger.error(f"Ошибка при получении предельной формы 3D: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении предельной формы: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
