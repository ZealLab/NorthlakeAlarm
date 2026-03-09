#!/bin/bash
set -e

# Check if the port is already in use and forcefully kill it before starting
if command -v fuser >/dev/null 2>&1; then
    echo "Ensuring port 8081 is free..."
    fuser -k 8081/tcp 2>/dev/null || true
fi

# Trap Ctrl+C (SIGINT) and ensure the entire process group is killed cleanly
cleanup() {
    echo -e "\nCaught signal. Terminating server..."
    trap - SIGINT SIGTERM EXIT
    kill 0 2>/dev/null
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# Build the frontend if the dist folder is missing (due to .gitignore)
echo "Checking frontend build..."
if [ ! -d "/home/rbowen/Repos/NorthlakeAlarm/frontend/dist" ]; then
    echo "Frontend dist not found. Building..."
    cd /home/rbowen/Repos/NorthlakeAlarm/frontend
    npm install
    npm run build
fi

# Start the uvicorn server serving backend API and static frontend
echo "Starting NorthlakeAlarm backend..."
if [ ! -d "/home/rbowen/Repos/NorthlakeAlarm/backend/venv" ]; then
    echo "Creating virtual environment..."
    cd /home/rbowen/Repos/NorthlakeAlarm
    python3 -m venv --system-site-packages backend/venv
    source backend/venv/bin/activate
    pip install -r requirements.txt
else
    source /home/rbowen/Repos/NorthlakeAlarm/backend/venv/bin/activate
fi

cd /home/rbowen/Repos/NorthlakeAlarm/backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8081 --reload
