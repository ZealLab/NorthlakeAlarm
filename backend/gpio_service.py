from gpiozero import Button
from gpiozero.pins.mock import MockFactory, MockPWMPin
import gpiozero
from state_manager import global_state_manager
import asyncio
import logging
import os

class GPIOService:
    def __init__(self):
        self.pins_mapping = {
            1: 17,
            2: 27,
            3: 22,
            4: 23,
            5: 24,
            6: 25
        }
        self.buttons = {}
        self.loop = None

    def start(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop
        
        # If not running on actual hardware, fallback to MockFactory for testing
        try:
            # Test if native pin factory works
            import RPi.GPIO
        except ImportError:
            logging.info("RPi.GPIO not found, falling back to mock pin factory for development.")
            gpiozero.Device.pin_factory = MockFactory()

        for zone_id, pin in self.pins_mapping.items():
            try:
                # Assuming NC (Normally Closed) sensors: Button pressed (low voltage) = SECURE
                btn = Button(pin, pull_up=True, bounce_time=0.05)
                btn.when_pressed = lambda z=zone_id: self._on_secure(z)
                btn.when_released = lambda z=zone_id: self._on_tripped(z)
                self.buttons[zone_id] = btn
                logging.info(f"Initialized Zone {zone_id} on GPIO {pin}")
            except Exception as e:
                logging.error(f"Failed to initialize Zone {zone_id} on GPIO {pin}: {e}")

    def _on_tripped(self, zone_id):
        if self.loop:
            asyncio.run_coroutine_threadsafe(
                global_state_manager.handle_zone_change(zone_id, True), 
                self.loop
            )

    def _on_secure(self, zone_id):
        if self.loop:
            asyncio.run_coroutine_threadsafe(
                global_state_manager.handle_zone_change(zone_id, False), 
                self.loop
            )

gpio_service = GPIOService()
