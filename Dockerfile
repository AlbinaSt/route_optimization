# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Устанавливаем системные зависимости для OSMnx и GDAL
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgeos-dev \
    libspatialindex-dev \
    python3-dev \
    gdal-bin \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем всё приложение
COPY app.py .
COPY templates/ ./templates/

# Открываем порт (стандартный порт Flask)
EXPOSE 5000

# Переменные окружения для Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Запускаем приложение
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]