import asyncio
import json
from datetime import datetime, timezone
from enum import Enum
import logging

# We will lazily import httpx or use a local function so it doesn't break if not installed correctly yet
import httpx

class SystemState(Enum):
    DISARMED = "DISARMED"
    ARMED_PARTIAL = "ARMED_PARTIAL"
    ARMED_FULL = "ARMED_FULL"

class StateManager:
    def __init__(self):
        self.state = SystemState.DISARMED
        self.zone_states = {i: "SECURE" for i in range(1, 7)}
        self.entry_delay_task = None
        self.webhook_url = None
        self.ws_clients = set()
    
    async def broadcast_state(self):
        message = {
            "type": "state_update",
            "system_state": self.state.value,
            "zones": self.zone_states
        }
        str_msg = json.dumps(message)
        for client in list(self.ws_clients):
            try:
                await client.send_text(str_msg)
            except Exception:
                self.ws_clients.discard(client)

    async def handle_zone_change(self, zone_id: int, is_tripped: bool):
        new_state = "TRIPPED" if is_tripped else "SECURE"
        if self.zone_states[zone_id] == new_state:
            return
        
        self.zone_states[zone_id] = new_state
        await self.broadcast_state()

        if is_tripped:
            await self._process_trip(zone_id)

    async def _process_trip(self, zone_id: int):
        if self.state == SystemState.DISARMED:
            return
            
        if self.state == SystemState.ARMED_PARTIAL and zone_id > 4:
            # 1-4 armed, 5-6 ignored
            return

        # Entry Delay for Zone 6
        if zone_id == 6:
            if not self.entry_delay_task:
                self.entry_delay_task = asyncio.create_task(self._entry_delay_countdown())
            return

        await self.trigger_alarm(zone_id)

    async def _entry_delay_countdown(self):
        await asyncio.sleep(30) # 30 seconds entry delay
        if self.state != SystemState.DISARMED:
            await self.trigger_alarm(6)
        self.entry_delay_task = None

    async def trigger_alarm(self, zone_id: int):
        logging.warning(f"ALARM TRIGGERED on Zone {zone_id}")
        if self.webhook_url:
            payload = {
                "zone_id": zone_id,
                "status": "ALARM",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(self.webhook_url, json=payload)
            except Exception as e:
                logging.error(f"Failed to trigger webhook: {e}")

global_state_manager = StateManager()
