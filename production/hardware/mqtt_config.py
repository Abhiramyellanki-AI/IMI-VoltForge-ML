"""
Phase F: Hardware IoT Bridge
mqtt_config.py — MQTT broker configuration and topic map.

Environment variables override defaults:
  MQTT_HOST    default: localhost
  MQTT_PORT    default: 1883
  API_URL      default: http://localhost:8000
"""
import os

# ─── MQTT Broker ──────────────────────────────────────────────────────────────
MQTT_HOST     = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT     = int(os.getenv("MQTT_PORT", "1883"))
MQTT_KEEPALIVE = 60
MQTT_CLIENT_ID = "imi-iot-bridge"

# ─── API Endpoint ─────────────────────────────────────────────────────────────
API_BASE_URL  = os.getenv("API_URL", "http://localhost:8000")

# ─── Inbound Sensor Topics (subscribe) ────────────────────────────────────────
TOPIC_TEMP     = "lab/sensors/temp"        # payload: float °C
TOPIC_PRESSURE = "lab/sensors/pressure"    # payload: float bar
TOPIC_SMILES   = "lab/sensors/smiles"      # payload: SMILES string (optional override)

# ─── Outbound Setpoint Topics (publish) ───────────────────────────────────────
TOPIC_SETPOINT_TEMP  = "lab/setpoints/temp"    # payload: float °C (corrective)
TOPIC_SETPOINT_CRYST = "lab/setpoints/cryst"   # payload: float fraction
TOPIC_STATUS         = "lab/status/eb"          # payload: JSON {predicted_eb, good_fit}

# ─── Control Loop Parameters ──────────────────────────────────────────────────
LOOP_INTERVAL_SEC  = 5       # seconds between sensor poll → predict → correct → publish
DESIRED_EB         = 600.0   # MV/m — target Eb for the correction loop
CORRECTION_DEADBAND = 20.0   # MV/m — only correct if |current - desired| > deadband

# ─── Default Polymer (fallback if no SMILES received via MQTT) ────────────────
DEFAULT_SMILES = "CC(F)(C(F)(F)F)CC(F)(I)"
