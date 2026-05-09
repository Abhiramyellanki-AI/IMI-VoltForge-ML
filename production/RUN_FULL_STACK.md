# IMI Polymer Informatics v2.0 — Ubuntu Run Guide

## Prerequisites

| Requirement | Minimum Version | Check Command |
|---|---|---|
| Ubuntu | 20.04 LTS or later | `lsb_release -a` |
| Python | 3.10+ | `python3 --version` |
| pip | 23+ | `pip3 --version` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |

---

## Step 0 — Transfer / Clone the Project

If you're copying from Windows, transfer the project to your Ubuntu machine.
The project should live at `~/IMI` (or any path you choose).

```bash
# Option A: copy via SCP from Windows
scp -r /mnt/a/IMI user@ubuntu-ip:~/IMI

# Option B: clone from Git (if pushed)
git clone <your-repo-url> ~/IMI
```

---

## Step 1 — One-Time Setup

Run this **once** to install all system packages, Python venv, Node modules,
and train the model:

```bash
cd ~/IMI
bash production/setup.sh
```

This script does **all** of the following automatically:
1. `sudo apt-get install python3 python3-venv python3-pip nodejs npm build-essential`
2. Creates `~/IMI/venv/` Python virtual environment
3. `pip install -r production/backend/requirements.txt`
4. `pip install -r production/hardware/requirements_hw.txt`
5. `npm install` in `production/frontend/`
6. Runs `python3 code_7_train_model.py` if `mlp_pipeline.pkl` is missing

---

## Step 2 — Start the Full Stack

### Option A — One command (recommended, uses tmux)
```bash
# Install tmux if you don't have it
sudo apt-get install -y tmux

# Launch backend + frontend in split panes
cd ~/IMI
bash production/start_all.sh
```

You'll see a tmux session with:
- **Left pane**: FastAPI backend (uvicorn)
- **Right pane**: Vite React frontend (npm run dev)

Press `Ctrl+B` then `D` to detach. `tmux attach -t imi` to re-attach.

---

### Option B — Two separate terminals

**Terminal 1 — Backend:**
```bash
cd ~/IMI
bash production/start_backend.sh
```

**Terminal 2 — Frontend:**
```bash
cd ~/IMI
bash production/start_frontend.sh
```

---

### Option C — Manual (full control)

```bash
# Activate virtual environment
cd ~/IMI
source venv/bin/activate

# Start backend (MUST run from ~/IMI — not from production/backend/)
uvicorn production.backend.main:app --reload --host 0.0.0.0 --port 8000

# In a new terminal — start frontend
cd ~/IMI/production/frontend
npm run dev
```

---

## Step 3 — (Optional) IoT Bridge

```bash
cd ~/IMI
source venv/bin/activate
cd production/hardware

# Mock mode — no hardware or MQTT broker needed
python3 iot_bridge.py --mock

# Single poll test
python3 iot_bridge.py --mock --once

# Live mode (requires Mosquitto MQTT broker running)
sudo apt-get install -y mosquitto mosquitto-clients
sudo systemctl start mosquitto
python3 iot_bridge.py
```

---

## Step 4 — Retrain the Model (Phase A)

If you want to retrain with the improved MLP + GBR ensemble:

```bash
cd ~/IMI
source venv/bin/activate
python3 code_7_train_model.py
```

Outputs: `mlp_pipeline.pkl`, `ensemble_pipeline.pkl`, updated `Final_Report.md`, and 3 plots.

---

## Access Points

| Service | URL |
|---|---|
| React Frontend | http://localhost:5173 |
| FastAPI Backend | http://localhost:8000 |
| Swagger API Docs | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Health Check | http://localhost:8000/health |

---

## API Quick Reference

```bash
# Health check
curl http://localhost:8000/health

# Forward prediction
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"smiles":"CC(F)(C(F)(F)F)CC(F)(I)", "processing_temp_c":220, "crystallinity":0.45}'

# Inverse design
curl -X POST http://localhost:8000/api/inverse-design \
  -H "Content-Type: application/json" \
  -d '{"smiles":"CC(F)(C(F)(F)F)CC(F)(I)", "target_eb":700}'

# Conditional search
curl -X POST http://localhost:8000/api/conditional-search \
  -H "Content-Type: application/json" \
  -d '{"target_eb":600, "polymer_class":"PVDF", "top_k":5}'

# Digital Twin predict
curl -X POST http://localhost:8000/api/twin/predict \
  -H "Content-Type: application/json" \
  -d '{"smiles":"CC(F)(C(F)(F)F)CC(F)(I)", "temperature":235, "pressure_bar":4.5}'

# Digital Twin simulate (no body needed)
curl http://localhost:8000/api/twin/simulate
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'config'` | Run uvicorn from `~/IMI/`, not from `production/backend/` |
| `ModuleNotFoundError: No module named 'production'` | Same — always run from `~/IMI/` |
| `No model files found` | Run `python3 code_7_train_model.py` from `~/IMI/` |
| `Dataset not found` | Run `python3 code_6_main.py` from `~/IMI/` |
| Port 8000 already in use | `kill $(lsof -t -i:8000)` |
| Port 5173 already in use | `kill $(lsof -t -i:5173)` |
| `rdkit` install fails | `pip install rdkit` (not `rdkit-pypi` on newer Python) |
| npm permission error | Never use `sudo npm` — fix: `sudo chown -R $USER ~/.npm` |

---

## File Structure

```
~/IMI/
├── config.py                          # Shared constants + CollinearityDropper
├── code_1_generate.py                 # 720 polymer SMILES generation
├── code_2_structural.py               # 40 RDKit structural features
├── code_3_polybert.py                 # 600-dim PolyBERT embeddings
├── code_4_physical.py                 # 40 RDKit physical features
├── code_5_morgan.py                   # 1024-bit Morgan fingerprints
├── code_6_main.py                     # Dataset aggregation
├── code_7_train_model.py              # MLP + GBR ensemble training (Phase A)
├── code_8_inverse_design.py           # Standalone CLI optimizer
├── code_9_generate_report.py          # Presentation CSV report
├── code_10_conditional_search.py      # Similarity search engine (Phase B)
├── mlp_pipeline.pkl                   # Trained MLP model
├── ensemble_pipeline.pkl              # Trained ensemble model (Phase A)
├── ready_polymer_dataset.csv          # 720 × 1788 feature matrix
└── production/
    ├── setup.sh                       # ← ONE-TIME SETUP
    ├── start_all.sh                   # ← START EVERYTHING
    ├── start_backend.sh               # Backend only
    ├── start_frontend.sh              # Frontend only
    ├── RUN_FULL_STACK.md              # This file
    ├── backend/
    │   ├── main.py                    # FastAPI app
    │   ├── requirements.txt           # Python deps
    │   ├── core/model_loader.py       # Singleton model cache
    │   ├── models/schemas.py          # Pydantic schemas
    │   └── routers/
    │       ├── predict.py             # POST /api/predict
    │       ├── inverse_design.py      # POST /api/inverse-design
    │       ├── conditional_generation.py  # POST /api/conditional-search
    │       └── digital_twin.py        # POST /api/twin/*
    ├── frontend/                      # Vite + React + TypeScript
    │   └── src/
    │       ├── api/client.ts          # Typed API wrappers
    │       ├── App.tsx                # Root component + routing
    │       ├── index.css              # Glassmorphism design system
    │       ├── components/Navbar.tsx
    │       └── pages/
    │           ├── Dashboard.tsx
    │           ├── InverseDesign.tsx
    │           ├── ConditionalSearch.tsx
    │           ├── DigitalTwin.tsx
    │           └── HardwareMonitor.tsx
    └── hardware/
        ├── iot_bridge.py              # MQTT IoT bridge (Phase F)
        ├── mqtt_config.py             # Topic map + broker config
        ├── requirements_hw.txt        # paho-mqtt, httpx, pyserial
        └── README_hardware.md         # Arduino/RPi wiring guide
```
