@echo off
set BACKEND_DIR=%~dp0backend
set FRONTEND_DIR=%~dp0frontend

echo ==========================================
echo   HALE-Potter Launcher
echo ==========================================
echo.

echo [1/2] Starting Backend...
cd /d "%BACKEND_DIR%"
if not exist venv (
    echo Creating Python venv...
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -q -r requirements.txt
start "HALE-Potter Backend" cmd /k "cd /d %BACKEND_DIR% && venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000 --host 0.0.0.0"

echo [2/2] Starting Frontend...
cd /d "%FRONTEND_DIR%"
if not exist node_modules (
    echo Installing npm packages...
    npm install
)
start "HALE-Potter Frontend" cmd /k "cd /d %FRONTEND_DIR% && npm run dev"

echo.
echo ==========================================
echo Services started!
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo ==========================================
pause
