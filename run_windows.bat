@echo off
echo === Установка виртуального окружения ===
python -m venv .venv
call .venv\Scripts\activate

echo === Установка зависимостей ===
pip install --upgrade pip
pip install -r backend\requirements.txt
pip install -r frontend\requirements.txt

set FASTAPI_URL=http://localhost:8000
set STREAMLIT_BROWSER_GATHER_USAGE_STATS=false   

echo === Запуск FastAPI (бэкенд) ===
start "FastAPI" /B uvicorn backend.app.main:app --host 0.0.0.0 --port 8000

echo === Запуск Streamlit (фронтенд) ===
$env:STREAMLIT_BROWSER_GATHER_USAGE_STATS="false"
start "Streamlit" /B streamlit run frontend\dashboard.py --server.port=8501

echo === Приложение запущено ===
echo FastAPI:  http://localhost:8000
echo Streamlit: http://localhost:8501
echo Для остановки закройте все окна командной строки.
pause