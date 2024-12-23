#!/bin/bash

# Сборка и запуск контейнеров в фоновом режиме
echo "Building and starting services..."
docker-compose up --build -d

# Ожидание, пока база данных не будет доступна
echo "Waiting for PostgreSQL to be ready..."
until docker-compose exec db pg_isready -U user -h db -p 5432 >/dev/null 2>&1; do
  echo "Waiting for PostgreSQL to be ready..."
  sleep 2
done

# Запуск миграций
echo "Running database migrations..."
docker-compose exec backend python -c "from app import init_db; init_db()"

echo "Services are up and running!"
