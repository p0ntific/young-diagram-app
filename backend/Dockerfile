FROM python:3.9-slim

WORKDIR /app

# Копирование и установка Python-зависимостей
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
RUN pip install gunicorn==20.1.0 fastapi uvicorn

# Копирование исходных файлов
COPY __init__.py .
COPY api.py .
COPY diagrams2d/ diagrams2d/
COPY diagrams3d/ diagrams3d/
COPY common/ common/

# Создание директорий для результатов симуляций
RUN mkdir -p results_2d results_3d

# Открываем порт, который будет использоваться API
EXPOSE 8000

# Команда для запуска API при старте контейнера
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"] 