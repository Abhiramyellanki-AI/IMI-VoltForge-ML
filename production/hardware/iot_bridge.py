"""
Phase F: Hardware IoT Bridge
iot_bridge.py — Closed-loop control script.

Architecture:
  read_sensors()       → MQTT subscribe (temp, pressure) OR mock random values
  post_telemetry()     → POST /api/twin/predict → TwinPredictionResponse
  run_correction()     → POST /api/twin/correct → CorrectionResponse (if Eb off-target)
  write_setpoints()    → MQTT publish corrective setpoints
  run_control_loop()   → main loop (default: 5s interval)

Run modes:
  python iot_bridge.py             # live MQTT (requires Mosquitto broker)
  python iot_bridge.py --mock      # mock sensor values (no MQTT required)
  python iot_bridge.py --mock --once  # single poll then exit
"""
import sys
import time
import json
import argparse
import random
import logging
from typing import Optional, Tuple
from datetime import datetime

import httpx

import mqtt_config as cfg

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level  = logging.INFO,
    format = '%(asctime)s [%(levelname)s] %(message)s',
    datefmt= '%H:%M:%S',
)
log = logging.getLogger("iot_bridge")

# ─── MQTT Client (optional) ───────────────────────────────────────────────────
try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    log.warning("paho-mqtt not installed. Run with --mock or: pip install paho-mqtt")
    MQTT_AVAILABLE = False

# Shared state updated by MQTT callbacks
_sensor_state = {
    "temp":     200.0,
    "pressure": 5.0,
    "smiles":   cfg.DEFAULT_SMILES,
}

def _on_message(client, userdata, msg):
    """MQTT message callback — updates shared sensor state."""
    topic   = msg.topic
    payload = msg.payload.decode("utf-8").strip()
    try:
        if topic == cfg.TOPIC_TEMP:
            _sensor_state["temp"] = float(payload)
            log.debug(f"  Sensor temp update: {_sensor_state['temp']}°C")
        elif topic == cfg.TOPIC_PRESSURE:
            _sensor_state["pressure"] = float(payload)
            log.debug(f"  Sensor pressure update: {_sensor_state['pressure']} bar")
        elif topic == cfg.TOPIC_SMILES:
            _sensor_state["smiles"] = payload
            log.debug(f"  Polymer SMILES update: {payload[:40]}...")
    except ValueError as e:
        log.warning(f"  Bad sensor payload on {topic}: {payload} ({e})")


def connect_mqtt() -> Optional[object]:
    """Connect to MQTT broker and subscribe to sensor topics."""
    if not MQTT_AVAILABLE:
        return None
    client = mqtt.Client(client_id=cfg.MQTT_CLIENT_ID)
    client.on_message = _on_message
    try:
        client.connect(cfg.MQTT_HOST, cfg.MQTT_PORT, cfg.MQTT_KEEPALIVE)
        client.subscribe([(cfg.TOPIC_TEMP, 0), (cfg.TOPIC_PRESSURE, 0), (cfg.TOPIC_SMILES, 0)])
        client.loop_start()
        log.info(f"Connected to MQTT broker at {cfg.MQTT_HOST}:{cfg.MQTT_PORT}")
        return client
    except Exception as e:
        log.error(f"MQTT connection failed: {e}. Running without MQTT.")
        return None


# ─── Sensor Read ──────────────────────────────────────────────────────────────

def read_sensors(mock: bool = False) -> Tuple[float, float, str]:
    """
    Returns (temperature_c, pressure_bar, smiles).

    In mock mode: applies small random drift to simulate real sensor jitter.
    In live mode:  returns values from _sensor_state (updated by MQTT callbacks).
    """
    if mock:
        # Apply Gaussian drift around current values
        temp     = max(100.0, min(300.0, _sensor_state["temp"]     + random.gauss(0, 5)))
        pressure = max(0.5,   min(20.0,  _sensor_state["pressure"] + random.gauss(0, 0.5)))
        _sensor_state["temp"]     = temp
        _sensor_state["pressure"] = pressure
        return temp, pressure, _sensor_state["smiles"]

    return _sensor_state["temp"], _sensor_state["pressure"], _sensor_state["smiles"]


# ─── API Calls ────────────────────────────────────────────────────────────────

def post_telemetry(smiles: str, temperature: float, pressure_bar: float) -> Optional[dict]:
    """POST to /api/twin/predict. Returns response dict or None on failure."""
    url     = f"{cfg.API_BASE_URL}/api/twin/predict"
    payload = {"smiles": smiles, "temperature": temperature, "pressure_bar": pressure_bar}
    try:
        resp = httpx.post(url, json=payload, timeout=10.0)
        resp.raise_for_status()
        return resp.json()
    except httpx.ConnectError:
        log.error(f"  API unreachable at {cfg.API_BASE_URL}. Start the FastAPI backend.")
        return None
    except Exception as e:
        log.error(f"  POST /api/twin/predict failed: {e}")
        return None


def run_correction(smiles: str, current_eb: float, current_temp: float, current_cryst: float) -> Optional[dict]:
    """POST to /api/twin/correct. Returns correction dict or None."""
    url     = f"{cfg.API_BASE_URL}/api/twin/correct"
    payload = {
        "smiles":        smiles,
        "current_eb":    current_eb,
        "desired_eb":    cfg.DESIRED_EB,
        "current_temp":  current_temp,
        "current_cryst": current_cryst,
    }
    try:
        resp = httpx.post(url, json=payload, timeout=15.0)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        log.error(f"  POST /api/twin/correct failed: {e}")
        return None


# ─── Setpoint Write ───────────────────────────────────────────────────────────

def write_setpoints(
    mqtt_client,
    delta_temp_c: float,
    delta_cryst: float,
    rec_temp: float,
    rec_cryst: float,
    predicted_eb: float,
    good_fit: bool,
):
    """
    Publishes corrective setpoints and status to MQTT.
    If mqtt_client is None (mock mode), just logs to console.
    """
    setpoint_payload = json.dumps({
        "recommended_temp_c":    round(rec_temp, 2),
        "recommended_cryst":     round(rec_cryst, 4),
        "delta_temp_c":          round(delta_temp_c, 2),
        "delta_cryst":           round(delta_cryst, 4),
        "timestamp":             datetime.utcnow().isoformat(),
    })
    status_payload = json.dumps({
        "predicted_eb": round(predicted_eb, 2),
        "good_fit":     good_fit,
        "timestamp":    datetime.utcnow().isoformat(),
    })

    if mqtt_client is not None:
        mqtt_client.publish(cfg.TOPIC_SETPOINT_TEMP,  str(rec_temp))
        mqtt_client.publish(cfg.TOPIC_SETPOINT_CRYST, str(rec_cryst))
        mqtt_client.publish(cfg.TOPIC_STATUS,          status_payload)
        log.info(f"  → Published setpoints to MQTT: Temp={rec_temp}°C, Cryst={rec_cryst:.3f}")
    else:
        log.info(f"  [MOCK PUBLISH] {cfg.TOPIC_SETPOINT_TEMP}: {rec_temp}°C")
        log.info(f"  [MOCK PUBLISH] {cfg.TOPIC_SETPOINT_CRYST}: {rec_cryst:.4f}")
        log.info(f"  [MOCK PUBLISH] {cfg.TOPIC_STATUS}: {status_payload}")


# ─── Main Control Loop ────────────────────────────────────────────────────────

def run_control_loop(mock: bool = False, once: bool = False):
    """
    Main IoT bridge control loop.

    Each iteration:
      1. Read sensors (temp, pressure, smiles)
      2. POST telemetry → get predicted Eb
      3. If |Eb - desired| > deadband: POST correction → get ΔTemp, ΔCryst
      4. Publish setpoints to MQTT
      5. Wait interval_sec
    """
    mqtt_client = None if mock else connect_mqtt()

    log.info("=" * 56)
    log.info("  IMI IoT Bridge — Phase F Control Loop Starting")
    log.info(f"  API:          {cfg.API_BASE_URL}")
    log.info(f"  Desired Eb:   {cfg.DESIRED_EB} MV/m")
    log.info(f"  Deadband:     ±{cfg.CORRECTION_DEADBAND} MV/m")
    log.info(f"  Interval:     {cfg.LOOP_INTERVAL_SEC}s")
    log.info(f"  Mode:         {'MOCK (no MQTT)' if mock else 'LIVE MQTT'}")
    log.info("=" * 56)

    iteration = 0

    while True:
        iteration += 1
        log.info(f"\n── Iteration {iteration} ──────────────────────────────────")

        # Step 1: Read sensors
        temp, pressure, smiles = read_sensors(mock=mock)
        log.info(f"  Sensors: T={temp:.1f}°C | P={pressure:.2f}bar | SMILES={smiles[:30]}...")

        # Step 2: Predict Eb
        pred = post_telemetry(smiles, temp, pressure)
        if pred is None:
            log.warning("  Skipping iteration — API unavailable.")
            if once: break
            time.sleep(cfg.LOOP_INTERVAL_SEC)
            continue

        predicted_eb   = pred["predicted_eb"]
        good_fit       = pred["good_fit"]
        est_cryst      = pred["estimated_crystallinity"]
        log.info(f"  Predicted Eb: {predicted_eb:.1f} MV/m | Good Fit: {good_fit} | χ={est_cryst:.3f}")

        # Step 3: Correct if outside deadband
        eb_error = abs(predicted_eb - cfg.DESIRED_EB)
        if eb_error > cfg.CORRECTION_DEADBAND:
            log.info(f"  Eb error {eb_error:.1f} MV/m > deadband {cfg.CORRECTION_DEADBAND} MV/m → running correction")
            corr = run_correction(smiles, predicted_eb, temp, est_cryst)
            if corr:
                log.info(f"  Correction: ΔT={corr['delta_temp_c']:+.1f}°C | Δχ={corr['delta_crystallinity']:+.4f} | Projected Eb={corr['projected_eb']:.1f} MV/m")
                write_setpoints(
                    mqtt_client    = mqtt_client,
                    delta_temp_c   = corr["delta_temp_c"],
                    delta_cryst    = corr["delta_crystallinity"],
                    rec_temp       = corr["recommended_temp_c"],
                    rec_cryst      = corr["recommended_crystallinity"],
                    predicted_eb   = predicted_eb,
                    good_fit       = good_fit,
                )
        else:
            log.info(f"  Eb within deadband (error={eb_error:.1f} MV/m) — no correction needed.")
            write_setpoints(mqtt_client, 0.0, 0.0, temp, est_cryst, predicted_eb, good_fit)

        if once:
            log.info("\nSingle-shot mode complete.")
            break

        log.info(f"  Sleeping {cfg.LOOP_INTERVAL_SEC}s...")
        time.sleep(cfg.LOOP_INTERVAL_SEC)

    if mqtt_client:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        log.info("MQTT client disconnected.")


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IMI IoT Bridge — Phase F Hardware Integration")
    parser.add_argument("--mock",     action="store_true", help="Use mock sensor values (no MQTT required)")
    parser.add_argument("--once",     action="store_true", help="Run a single control iteration then exit")
    parser.add_argument("--interval", type=int, default=None, help="Override loop interval (seconds)")
    args = parser.parse_args()

    if args.interval:
        cfg.LOOP_INTERVAL_SEC = args.interval

    try:
        run_control_loop(mock=args.mock, once=args.once)
    except KeyboardInterrupt:
        log.info("\nIoT bridge stopped by user (Ctrl+C).")
        sys.exit(0)
