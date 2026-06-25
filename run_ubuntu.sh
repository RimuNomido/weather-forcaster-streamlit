#!/bin/bash

# Цветной вывод для красоты
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Установка виртуального окружения ===${NC}"
python3 -m venv .venv
source .venv/bin/activate

echo -e "${GREEN}=== Установка зависимостей ===${NC}"
pip install --upgrade pip
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt

export FASTAPI_URL="http://localhost:8000"
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false 

echo -e "${GREEN}=== Запуск FastAPI (бэкенд) ===${NC}"
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo -e "${GREEN}=== Запуск Streamlit (фронтенд) ===${NC}"
streamlit run frontend/dashboard.py --server.port=8501 &
FRONTEND_PID=$!

echo -e "${GREEN}=== Приложение запущено ===${NC}"
echo "FastAPI:  http://localhost:8000"
echo "Streamlit: http://localhost:8501"
echo "Для остановки нажмите Ctrl+C"

# Ждём завершения (чтобы скрипт не завершался сразу)
wait $BACKEND_PID $FRONTEND_PID