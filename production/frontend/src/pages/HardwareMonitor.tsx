import { useState } from 'react';
import { api, type SimulateResponse } from '../api/client';

const IOT_STEPS = [
  { icon: '📡', label: 'Read Sensors', desc: 'MQTT topics lab/sensors/temp + lab/sensors/pressure → TelemetryInput' },
  { icon: '🔮', label: 'POST /api/twin/predict', desc: 'HTTP → Digital Twin endpoint returns predicted Eb + good_fit flag' },
  { icon: '⟳',  label: 'POST /api/twin/correct', desc: 'If Eb off-target, optimizer returns ΔTemp + ΔCryst setpoints' },
  { icon: '📤', label: 'Write Setpoints', desc: 'Publish corrective setpoints to MQTT lab/setpoints/temp + lab/setpoints/cryst' },
  { icon: '⏱',  label: 'Wait interval (5s)', desc: 'Loop repeats every 5 seconds for continuous closed-loop control' },
];

export default function HardwareMonitor() {
  const [simResult,   setSimResult]   = useState<SimulateResponse | null>(null);
  const [loading,     setLoading]     = useState(false);
  const [error,       setError]       = useState('');
  const [loopRunning, setLoopRunning] = useState(false);
  const [loopLog,     setLoopLog]     = useState<string[]>([]);

  const runSimulate = async () => {
    setLoading(true); setError('');
    try {
      const res = await api.twinSimulate();
      setSimResult(res);
    } catch (e: any) { setError(e.message ?? 'Simulation failed. Is the API running?'); }
    finally { setLoading(false); }
  };

  const mockLoopStep = async () => {
    const stamp = new Date().toLocaleTimeString();
    setLoopLog(prev => [`[${stamp}] Reading sensors...`, ...prev].slice(0, 20));
    try {
      const res = await api.twinSimulate();
      setLoopLog(prev => [
        `[${stamp}] Eb=${res.predicted_eb.toFixed(1)} MV/m | T=${res.temperature.toFixed(1)}°C | P=${res.pressure_bar}bar | ${res.good_fit ? '✓ Good Fit' : '✕ Below Threshold'}`,
        ...prev
      ].slice(0, 20));
    } catch {
      setLoopLog(prev => [`[${stamp}] ⚠ API unreachable`, ...prev].slice(0, 20));
    }
  };

  const toggleLoop = () => {
    if (loopRunning) {
      setLoopRunning(false);
    } else {
      setLoopRunning(true);
      setLoopLog([]);
      const id = setInterval(async () => {
        await mockLoopStep();
      }, 3000);
      // Store id on window for cleanup (simple approach without useRef)
      (window as any)._iotLoopId = id;
    }
  };

  if (!loopRunning && (window as any)._iotLoopId) {
    clearInterval((window as any)._iotLoopId);
    (window as any)._iotLoopId = null;
  }

  const ebColor = (eb: number) => eb >= 450 ? 'var(--accent-green)' : eb >= 300 ? 'var(--accent-amber)' : 'var(--accent-red)';

  return (
    <div className="fade-in">
      <div className="page-header">
        <h1 className="page-title">⚙ Hardware I/O Monitor</h1>
        <p className="page-subtitle">
          IoT bridge simulation — demonstrates the closed-loop control architecture connecting
          lab sensors → API → optimizer → equipment setpoints via MQTT.
        </p>
      </div>

      {/* Architecture Diagram */}
      <div className="section">
        <h2 className="section-title">◎ Control Loop Architecture</h2>
        <div className="card">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1.5rem', paddingBottom: '0.5rem' }}>
            {IOT_STEPS.map((step, i) => (
              <div key={i} style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '1.5rem', textAlign: 'center', position: 'relative' }}>
                <div style={{ position: 'absolute', top: '-10px', left: '-10px', width: '24px', height: '24px', background: 'var(--accent-orange)', color: 'white', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.75rem', fontWeight: 600 }}>{i + 1}</div>
                <div style={{ fontSize: '1.75rem', marginBottom: '0.75rem' }}>{step.icon}</div>
                <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.5rem' }}>{step.label}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>{step.desc}</div>
              </div>
            ))}
          </div>

          <div className="divider" style={{ margin: '2rem 0' }} />

          <div className="grid-2">
            <div>
              <div className="card-title">MQTT Topics</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', marginTop: '0.5rem' }}>
                {[
                  { dir: 'IN',  color: 'cyan',  topic: 'lab/sensors/temp' },
                  { dir: 'IN',  color: 'cyan',  topic: 'lab/sensors/pressure' },
                  { dir: 'OUT', color: 'amber', topic: 'lab/setpoints/temp' },
                  { dir: 'OUT', color: 'amber', topic: 'lab/setpoints/cryst' },
                ].map(t => (
                  <div key={t.topic} style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                    <span className={`badge badge-${t.color}`} style={{ minWidth: '36px', justifyContent: 'center' }}>{t.dir}</span>
                    <code style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{t.topic}</code>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <div className="card-title">Hardware Targets</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', marginTop: '0.5rem', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                <div>🍓 <strong>Raspberry Pi 4</strong> — MQTT bridge host</div>
                <div>⚡ <strong>Arduino / ESP32</strong> — Sensor reading + relay control</div>
                <div>🌡 <strong>DS18B20</strong> — Temperature probe (1-Wire)</div>
                <div>💧 <strong>MPX5700AP</strong> — Pressure transducer (0–700 kPa)</div>
                <div>📡 <strong>Mosquitto</strong> — MQTT broker (localhost:1883)</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Live Simulation */}
      <div className="section">
        <h2 className="section-title">▶ Live IoT Bridge Simulation</h2>
        <div className="grid-2" style={{ alignItems: 'start' }}>
          <div className="card">
            <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
              <button id="hw-simulate-btn" className="btn btn-primary" onClick={runSimulate} disabled={loading}>
                {loading ? <><span className="spinner" /> Polling...</> : '📡 Single Poll'}
              </button>
              <button id="hw-loop-btn" className={`btn ${loopRunning ? 'btn-amber' : 'btn-secondary'}`} onClick={toggleLoop}>
                {loopRunning ? '⏹ Stop Loop' : '▶ Start Control Loop (3s)'}
              </button>
            </div>

            {loopRunning && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '1rem' }}>
                <span className="status-dot online" />
                <span style={{ fontSize: '0.875rem', color: 'var(--accent-green)', fontWeight: 600 }}>Control loop active</span>
              </div>
            )}

            {error && <div className="error-banner" style={{ marginTop: '1rem' }}><span>⚠</span> {error}</div>}

            {simResult && (
              <div style={{ marginTop: '1.25rem' }}>
                <div className="card-title">Last Poll Result</div>
                <div style={{ marginTop: '0.5rem' }}>
                  <div style={{ fontSize: '2rem', fontWeight: 800, fontFamily: 'var(--font-mono)', color: ebColor(simResult.predicted_eb) }}>
                    {simResult.predicted_eb.toFixed(1)} <span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>MV/m</span>
                  </div>
                  <div style={{ display: 'flex', gap: '0.4rem', marginTop: '0.5rem', flexWrap: 'wrap' }}>
                    <span className="badge badge-cyan">T={simResult.temperature.toFixed(1)}°C</span>
                    <span className="badge badge-amber">P={simResult.pressure_bar}bar</span>
                    <span className="badge badge-green">χ={( simResult.estimated_crystallinity*100).toFixed(1)}%</span>
                    <span className={`badge ${simResult.good_fit ? 'badge-green' : 'badge-red'}`}>{simResult.good_fit ? '✓ Good Fit' : '✕ Below 450'}</span>
                  </div>
                  <div className="code-block" style={{ marginTop: '0.75rem', fontSize: '0.68rem' }}>
                    {simResult.smiles}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Console log */}
          <div className="card">
            <div className="card-title" style={{ marginBottom: '0.75rem' }}>IoT Bridge Console</div>
            <div style={{ background: 'var(--bg-base)', borderRadius: 'var(--radius-sm)', padding: '0.75rem', minHeight: '240px', maxHeight: '340px', overflowY: 'auto', border: '1px solid var(--border-subtle)', fontFamily: 'var(--font-mono)', fontSize: '0.72rem' }}>
              {loopLog.length === 0 ? (
                <div style={{ color: 'var(--text-muted)' }}>$ awaiting iot_bridge.py startup...</div>
              ) : (
                loopLog.map((line, i) => (
                  <div key={i} style={{ color: i === 0 ? 'var(--accent-green)' : 'var(--text-secondary)', marginBottom: '0.2rem', lineHeight: 1.5 }}>
                    {line}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Code Snippet */}
      <div className="section">
        <h2 className="section-title">⚙ Integration Script Reference</h2>
        <div className="card">
          <div className="card-title" style={{ marginBottom: '0.75rem' }}>production/hardware/iot_bridge.py</div>
          <div className="code-block" style={{ whiteSpace: 'pre-wrap', lineHeight: 1.7, fontSize: '0.72rem' }}>
{`# Run the IoT bridge:
python production/hardware/iot_bridge.py

# Or with custom API URL:
API_URL=http://192.168.1.10:8000 python iot_bridge.py

# Key functions:
#   read_sensors()    → polls MQTT for temp + pressure
#   post_telemetry()  → POST /api/twin/predict
#   run_correction()  → POST /api/twin/correct (if Eb off-target)
#   write_setpoints() → publishes ΔTemp, ΔCryst to MQTT
#   run_control_loop(interval_sec=5) → main entry`}
          </div>
        </div>
      </div>
    </div>
  );
}
