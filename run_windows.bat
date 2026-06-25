@echo off
cls

echo === Step 1: Virtual Environment ===
python -m venv .venv
call .venv\Scripts\activate

echo === Step 2: Dependencies ===
python -m pip install --upgrade pip
pip install -r backend\requirements.txt
pip install -r frontend\requirements.txt

echo === Step 3: Environment Variables ===
set FASTAPI_URL=http://localhost:8000
set STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
set PYTHONIOENCODING=utf-8

echo === Step 4: Starting FastAPI ===
start "FastAPI" /B uvicorn backend.app.main:app --host 0.0.0.0 --port 8000

echo === Step 5: Starting Streamlit ===
start "Streamlit" /B streamlit run frontend\dashboard.py --server.port=8501

echo === App is running! ===
echo FastAPI:   http://localhost:8000
echo Streamlit: http://localhost:8501
echo To stop everything, close this terminal window.
pause
