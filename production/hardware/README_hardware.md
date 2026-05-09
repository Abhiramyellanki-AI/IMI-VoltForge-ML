# Phase F — Hardware Integration Guide

## Overview
The `iot_bridge.py` script is a closed-loop control process that connects physical lab equipment to the IMI Digital Twin API. It reads sensor telemetry via MQTT, calls the FastAPI backend for Eb prediction and correction, then publishes corrective setpoints back to the equipment.

## Quick Start (Mock Mode — No Hardware Required)

```powershell
# Install dependencies
pip install -r requirements_hw.txt

# Run single poll (demo)
python iot_bridge.py --mock --once

# Run continuous loop at 5s interval
python iot_bridge.py --mock

# Custom interval
python iot_bridge.py --mock --interval 10
```

## Live Hardware Mode (Requires MQTT Broker)

```powershell
# 1. Install Mosquitto MQTT broker
#    Download: https://mosquitto.org/download/
#    Windows service starts automatically after install

# 2. Run with live MQTT
python iot_bridge.py

# 3. Override broker host/API URL via environment
$env:MQTT_HOST = "192.168.1.50"
$env:API_URL   = "http://192.168.1.10:8000"
python iot_bridge.py
```

## MQTT Topic Map

| Direction | Topic | Payload | Unit |
|---|---|---|---|
| IN  (subscribe) | `lab/sensors/temp`     | float | °C |
| IN  (subscribe) | `lab/sensors/pressure` | float | bar |
| IN  (subscribe) | `lab/sensors/smiles`   | string | SMILES |
| OUT (publish)   | `lab/setpoints/temp`   | float | °C |
| OUT (publish)   | `lab/setpoints/cryst`  | float | fraction |
| OUT (publish)   | `lab/status/eb`        | JSON  | {predicted_eb, good_fit} |

## Raspberry Pi + Arduino Wiring

```
[Arduino/ESP32] ──USB/UART──→ [Raspberry Pi 4]
  DS18B20 (temp, 1-Wire)          Mosquitto MQTT broker
  MPX5700AP (pressure, analog)    iot_bridge.py → IMI API
  Relay module (heater control)   ← lab/setpoints/temp
```

### Arduino Sketch Outline
```cpp
// Reads DS18B20 + MPX5700AP, publishes to MQTT every 2s
// Subscribes to lab/setpoints/temp → adjusts relay (heater on/off)
// Library: PubSubClient.h + OneWire.h + DallasTemperature.h
void loop() {
  float temp     = readDS18B20();
  float pressure = analogRead(A0) * (700.0 / 1023.0);  // MPX5700AP 0-700kPa
  client.publish("lab/sensors/temp",     String(temp).c_str());
  client.publish("lab/sensors/pressure", String(pressure / 100.0).c_str()); // kPa→bar
  client.loop();
  delay(2000);
}
```

## Control Loop Logic

```
Every 5 seconds:
  1. Read sensors (temp, pressure) from MQTT
  2. POST /api/twin/predict → get predicted_eb
  3. If |predicted_eb - desired_eb| > 20 MV/m (deadband):
       POST /api/twin/correct → get ΔTemp, ΔCryst
       Publish new setpoints to lab/setpoints/temp
  4. Publish status to lab/status/eb
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `MQTT_HOST` | `localhost` | MQTT broker IP |
| `MQTT_PORT` | `1883` | MQTT broker port |
| `API_URL` | `http://localhost:8000` | FastAPI backend URL |
