from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from gpio_service import gpio_service
from state_manager import global_state_manager, SystemState
import asyncio
import os
import json
import logging

app = FastAPI(title="NorthlakeAlarm Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Start the GPIO service attached to the current running event loop
    loop = asyncio.get_running_loop()
    gpio_service.start(loop)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    global_state_manager.ws_clients.add(websocket)
    # Send immediate state on connect
    await global_state_manager.broadcast_state()
    try:
        while True:
            data = await websocket.receive_text()
            try:
                cmd = json.loads(data)
                command_type = cmd.get("command")
                if command_type == "ARM_FULL":
                    global_state_manager.state = SystemState.ARMED_FULL
                elif command_type == "ARM_PARTIAL":
                    global_state_manager.state = SystemState.ARMED_PARTIAL
                elif command_type == "DISARM":
                    global_state_manager.state = SystemState.DISARMED
                    if global_state_manager.entry_delay_task:
                        global_state_manager.entry_delay_task.cancel()
                        global_state_manager.entry_delay_task = None
                await global_state_manager.broadcast_state()
            except Exception as e:
                logging.error(f"Error handling WS command: {e}")
    except WebSocketDisconnect:
        global_state_manager.ws_clients.remove(websocket)

@app.get("/api/status")
async def get_status():
    return {
        "state": global_state_manager.state.value,
        "zones": global_state_manager.zone_states
    }

@app.get("/api/metrics")
async def get_metrics():
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp = float(f.read()) / 1000.0
            temp_str = f"{temp:.1f}°C"
    except Exception:
        temp_str = "N/A"
    
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            hours = int(uptime_seconds // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            uptime_str = f"{hours}h{minutes}m"
    except Exception:
        uptime_str = "N/A"
        
    return {"temperature": temp_str, "uptime": uptime_str}

# Mount frontend build if it exists
frontend_path = os.path.join(os.path.dirname(__file__), "../frontend/dist")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
