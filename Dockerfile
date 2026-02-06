# Используем официальный образ Python 3.12 в минимальной версии
FROM python:3.12-slim

# Установка системных зависимостей, необходимых для сборки asyncpg/psycopg2
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь остальной код проекта в рабочую директорию
COPY . .

# Команду запуска (CMD) мы переопределим в docker-compose
