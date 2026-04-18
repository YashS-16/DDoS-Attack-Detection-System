#!/bin/bash

echo "========================================================"
echo "NetGuard Sentinel - DDoS Attack Detection System Booster"
echo "========================================================"

# Check for Python
if ! command -v python3 &> /dev/null
then
    echo "[ERROR] Python 3 could not be found. Please install it."
    exit
fi

# Check for Node.js
if ! command -v node &> /dev/null
then
    echo "[ERROR] Node.js could not be found. Please install it."
    exit
fi

# Setup Backend
echo "[INFO] Setting up the Python backend..."
if [ ! -d "venv" ]; then
    echo "[INFO] Creating Python virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate
echo "[INFO] Installing requirements (this might take a minute)..."
pip3 install -r requirements.txt > /dev/null 2>&1

# Start Backend in background
echo "[INFO] Starting Flask backend API..."
cd Backend && python3 app.py &
BACKEND_PID=$!
cd ..

# Setup Frontend
echo "[INFO] Setting up Vite frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "[INFO] Installing NPM dependencies..."
    npm install
fi

# Start Frontend in background
echo "[INFO] Starting React Dashboard..."
npm run dev -- --host &
FRONTEND_PID=$!

echo "========================================================"
echo "[SUCCESS] System is launching!"
echo "Backend API is running on PID $BACKEND_PID"
echo "Frontend Dashboard is running on PID $FRONTEND_PID"
echo "Press [CTRL+C] to stop both services."
echo "========================================================"

trap "echo '[INFO] Stopping services...'; kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
