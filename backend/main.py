import os
import time
import json
import logging
import paho.mqtt.client as mqtt
from gpiozero import Button

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("alarm-backend")

MQTT_BROKER = os.environ.get("MQTT_BROKER", "mosquitto")
MQTT_PORT = int(os.environ.get("MQTT_PORT", 1883))

ZONES = {
    1: {"pin": 17, "name": "Zone 1"},
    2: {"pin": 27, "name": "Zone 2"},
    3: {"pin": 22, "name": "Zone 3"},
    4: {"pin": 23, "name": "Zone 4"},
    5: {"pin": 24, "name": "Zone 5"},
    6: {"pin": 25, "name": "Zone 6"},
}

buttons = {}
client = mqtt.Client(client_id="alarm-backend")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected to MQTT Broker!")
        publish_discovery()
        # Publish initial state
        for z_id in ZONES:
            if z_id in buttons:
                state = "OFF" if buttons[z_id].is_pressed else "ON"
                publish_state(z_id, state)
    else:
        logger.error(f"Failed to connect, return code {rc}")

def publish_discovery():
    for z_id, info in ZONES.items():
        topic = f"homeassistant/binary_sensor/northlake_zone_{z_id}/config"
        payload = {
            "name": info["name"],
            "device_class": "window" if z_id != 6 else "door",
            "state_topic": f"northlake/zone/{z_id}/state",
            "unique_id": f"northlake_zone_{z_id}",
            "device": {
                "identifiers": ["northlake_alarm_panel"],
                "name": "Northlake Alarm Panel",
                "manufacturer": "Northlake",
                "model": "Pi 3B+"
            }
        }
        client.publish(topic, json.dumps(payload), retain=True)
    logger.info("Published HA Auto-Discovery payload for all zones.")

def publish_state(zone_id, state):
    topic = f"northlake/zone/{zone_id}/state"
    client.publish(topic, state, retain=True)
    logger.info(f"Zone {zone_id} state changed to {state}")

def setup_gpio():
    # Use BCM numbering (default for gpiozero)
    for z_id, info in ZONES.items():
        try:
            # pull_up=True means normally open switches (connected to ground) will read False when pressed (closed)
            # Depending on the wired hardware state, this might need to reverse (e.g., active high vs active low).
            # We assume active low: circuit closed = pin connected to GND = pressed
            btn = Button(info["pin"], pull_up=True, bounce_time=0.1)
            
            def make_press_handler(zid):
                return lambda: publish_state(zid, "OFF") # Secure
                
            def make_release_handler(zid):
                return lambda: publish_state(zid, "ON") # Tripped
                
            btn.when_pressed = make_press_handler(z_id)
            btn.when_released = make_release_handler(z_id)
            buttons[z_id] = btn
            logger.info(f"Registered GPIO for Zone {z_id} on pin {info['pin']}")
        except Exception as e:
            logger.error(f"Failed to setup pin for Zone {z_id}: {e}")

def main():
    logger.info("Starting Northlake Alarm Minimal MQTT Backend...")
    setup_gpio()

    client.on_connect = on_connect
    
    # Try to connect with retry logic
    connected = False
    while not connected:
        try:
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
            connected = True
        except Exception as e:
            logger.warning(f"Connection to MQTT failed: {e}. Retrying in 5s...")
            time.sleep(5)
            
    client.loop_forever()

if __name__ == "__main__":
    main()
