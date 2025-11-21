# Базовый образ
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Системные пакеты: ffmpeg + build deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копируем requirements и ставим зависимости
COPY requirements.txt /app/requirements.txt

# Можно отдельно подтянуть torch под CPU, чтобы whisper не чудил
RUN pip install --upgrade pip && \
    pip install torch==2.3.1 --index-url https://download.pytorch.org/whl/cpu && \
    pip install -r /app/requirements.txt

# Копируем исходники приложения
COPY . /app

# Порт uvicorn
EXPOSE 8000

# Команда запуска uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
