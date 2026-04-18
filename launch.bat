@echo off
echo ========================================================
echo NetGuard Sentinel - DDoS Attack Detection System Booster
echo ========================================================

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python 3 is not installed or not in PATH.
    pause
    exit /b
)

:: Check for Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH.
    pause
    exit /b
)

:: Setup Backend
echo [INFO] Setting up the Python backend...
if not exist "venv" (
    echo [INFO] Creating Python virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat
echo [INFO] Installing requirements (this might take a minute)...
pip install -r requirements.txt >nul 2>&1

:: Start Backend in a new window
echo [INFO] Starting Flask backend API...
start "NetGuard Backend API" cmd /k "venv\Scripts\activate.bat && cd Backend && python app.py"

:: Setup Frontend
echo [INFO] Setting up Vite frontend...
cd frontend
if not exist "node_modules" (
    echo [INFO] Installing NPM dependencies...
    cmd /c "npm install"
)

:: Start Frontend in a new window
echo [INFO] Starting React Dashboard...
start "NetGuard React Dashboard" cmd /k "npm run dev"

echo ========================================================
echo [SUCCESS] System is launching!
echo [INFO] Backend API is spinning up.
echo [INFO] Frontend Dashboard will open. Close the newly opened command windows to stop the servers later.
echo ========================================================
pause
