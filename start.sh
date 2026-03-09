#!/bin/bash
set -e

SCRIPT_DIR="$(dirname "$(realpath "$0")")"

# Install system dependencies if missing
if ! command -v node >/dev/null 2>&1 || ! command -v npm >/dev/null 2>&1 || ! command -v python3 >/dev/null 2>&1 || ! python3 -m venv -h >/dev/null 2>&1; then
    echo "Missing dependencies. Installing Python, Node, NPM, and Venv (requires sudo)..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-venv python3-pip nodejs npm
fi

# Set up systemd service if it doesn't exist
SERVICE_FILE="/etc/systemd/system/northlakealarm.service"
if [ ! -f "$SERVICE_FILE" ]; then
    echo "Systemd service not found. Creating and enabling northlakealarm.service (requires sudo)..."
    cat <<EOF | sudo tee "$SERVICE_FILE" > /dev/null
[Unit]
Description=Northlake Alarm System Dashboard
After=network.target

[Service]
User=$USER
WorkingDirectory=$SCRIPT_DIR
ExecStart=$SCRIPT_DIR/start.sh
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF
    sudo systemctl daemon-reload
    sudo systemctl enable northlakealarm.service
    echo "Northlake Alarm service configured and enabled to start on boot!"
fi

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
