import { useState, useEffect, useRef } from 'react';
import { api, type TwinPredictionResponse, type CorrectionResponse } from '../api/client';

const DEFAULT_SMILES = 'CC(F)(C(F)(F)F)CC(F)(I)';

export default function DigitalTwin() {
  const [smiles,      setSmiles]      = useState(DEFAULT_SMILES);
  const [temperature, setTemperature] = useState(220);
  const [pressure,    setPressure]    = useState(5.0);
  const [loading,     setLoading]     = useState(false);
  const [prediction,  setPrediction]  = useState<TwinPredictionResponse | null>(null);
  const [correction,  setCorrection]  = useState<CorrectionResponse | null>(null);
  const [desiredEb,   setDesiredEb]   = useState(600);
  const [history,     setHistory]     = useState<Array<{ time: string; temp: number; eb: number; good_fit: boolean }>>([]);
  const [error,       setError]       = useState('');
  const [autoMode,    setAutoMode]    = useState(false);
  const autoRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const estimatedCryst = Math.min(0.90, Math.max(0.10, 0.05 * pressure + 0.10));

  const runPredict = async (t = temperature, p = pressure) => {
    setLoading(true); setError(''); setCorrection(null);
    try {
      const res = await api.twinPredict({ smiles, temperature: t, pressure_bar: p });
      setPrediction(res);
      setHistory(prev => [{ time: new Date().toLocaleTimeString(), temp: t, eb: res.predicted_eb, good_fit: res.good_fit }, ...prev].slice(0, 12));
    } catch (e: any) { setError(e.message ?? 'Failed'); }
    finally { setLoading(false); }
  };

  const runCorrect = async () => {
    if (!prediction) return;
    setLoading(true); setError('');
    try {
      const res = await api.twinCorrect({ smiles, current_eb: prediction.predicted_eb, desired_eb: desiredEb, current_temp: prediction.temperature, current_cryst: prediction.estimated_crystallinity });
      setCorrection(res);
    } catch (e: any) { setError(e.message ?? 'Failed'); }
    finally { setLoading(false); }
  };

  useEffect(() => {
    if (autoMode) {
      autoRef.current = setInterval(() => {
        const newT = Math.min(300, Math.max(100, temperature + (Math.random() - 0.5) * 12));
        const newP = Math.min(20, Math.max(0.5, pressure + (Math.random() - 0.5) * 1.5));
        setTemperature(newT); setPressure(newP);
        runPredict(newT, newP);
      }, 2500);
    } else { if (autoRef.current) clearInterval(autoRef.current); }
    return () => { if (autoRef.current) clearInterval(autoRef.current); };
  }, [autoMode, temperature, pressure, smiles]);

  const ebColor = (eb: number) => eb >= 450 ? 'var(--accent-green)' : eb >= 300 ? 'var(--accent-amber)' : 'var(--accent-red)';

  return (
    <div className="fade-in">
      <div className="page-header">
        <h1 className="page-title">◎ Digital Twin</h1>
        <p className="page-subtitle">Real-time telemetry (Temp + Pressure) → E<sub>b</sub> prediction + corrective setpoints via L-BFGS-B feedback loop.</p>
      </div>

      <div className="grid-2" style={{ alignItems: 'start' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div className="card">
            <div className="card-title">Polymer SMILES</div>
            <input id="twin-smiles" className="form-input mono" value={smiles} onChange={e => setSmiles(e.target.value)} style={{ marginTop: '0.5rem' }} />
          </div>

          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <div className="card-title" style={{ marginBottom: 0 }}>🌡 Live Telemetry</div>
              <button className={`btn btn-sm ${autoMode ? 'btn-amber' : 'btn-secondary'}`} onClick={() => setAutoMode(a => !a)}>
                {autoMode ? '⏹ Stop' : '▶ Auto Simulate'}
              </button>
            </div>

            {[
              { label: 'Temperature', id: 'twin-temp', val: temperature, set: setTemperature, min: 100, max: 300, unit: '°C', color: 'cyan', pct: (temperature - 100) / 200 },
              { label: 'Pressure',    id: 'twin-pressure', val: pressure, set: setPressure, min: 0.5, max: 20, unit: ' bar', color: 'amber', pct: (pressure - 0.5) / 19.5 },
            ].map(s => (
              <div className="form-group" key={s.label} style={{ marginBottom: '1rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <label className="form-label">{s.label}</label>
                  <span style={{ fontFamily: 'var(--font-mono)', color: `var(--accent-${s.color})`, fontWeight: 700, fontSize: '0.9rem' }}>{s.val.toFixed(1)}{s.unit}</span>
                </div>
                <input id={s.id} type="range" className="range-slider" min={s.min} max={s.max} step={s.label === 'Temperature' ? 1 : 0.1} value={s.val} onChange={e => s.set(Number(e.target.value))} />
                <div className="gauge-track" style={{ marginTop: '0.25rem' }}><div className={`gauge-fill ${s.color}`} style={{ width: `${s.pct * 100}%` }} /></div>
              </div>
            ))}

            <div style={{ padding: '0.5rem 0.75rem', background: 'var(--bg-surface)', borderRadius: 'var(--radius-sm)', display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>Derived Crystallinity</span>
              <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-green)', fontWeight: 700 }}>{(estimatedCryst * 100).toFixed(1)}%</span>
            </div>

            <button id="twin-predict-btn" className="btn btn-primary btn-full" onClick={() => runPredict()} disabled={loading}>
              {loading ? <><span className="spinner" /> Processing...</> : '◎ Predict Eb'}
            </button>
          </div>

          {prediction && (
            <div className="card fade-in">
              <div className="card-title">Correction Loop — Desired Eb</div>
              <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', margin: '0.6rem 0 0.75rem' }}>
                <input id="twin-desired-eb" type="range" className="range-slider" min={200} max={800} step={10} value={desiredEb} onChange={e => setDesiredEb(Number(e.target.value))} />
                <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-cyan)', fontWeight: 700, minWidth: '70px' }}>{desiredEb} MV/m</span>
              </div>
              <button id="twin-correct-btn" className="btn btn-amber btn-full" onClick={runCorrect} disabled={loading}>
                {loading ? <><span className="spinner" /> Calculating...</> : '⟳ Get Corrective Setpoints'}
              </button>
            </div>
          )}

          {error && <div className="error-banner"><span>⚠</span> {error}</div>}
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {prediction ? (
            <div className="result-panel fade-in">
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                <div className="card-title">Twin Prediction</div>
                <span className={`badge ${prediction.good_fit ? 'badge-green' : 'badge-red'}`}>{prediction.good_fit ? '✓ Good Fit' : '✕ Below 450'}</span>
              </div>
              <div className="result-eb" style={{ color: ebColor(prediction.predicted_eb) }}>{prediction.predicted_eb.toFixed(1)}<span className="result-unit"> MV/m</span></div>
              <div style={{ display: 'flex', gap: '0.4rem', marginTop: '0.75rem', flexWrap: 'wrap' }}>
                {[`T=${prediction.temperature.toFixed(1)}°C`, `P=${prediction.pressure_bar}bar`, `χ=${(prediction.estimated_crystallinity * 100).toFixed(1)}%`, prediction.model_used].map(b => (
                  <span key={b} className="badge badge-cyan">{b}</span>
                ))}
              </div>
            </div>
          ) : (
            <div className="card" style={{ textAlign: 'center', padding: '2.5rem', color: 'var(--text-muted)' }}>
              <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>◎</div>
              <div style={{ fontSize: '0.875rem' }}>Adjust telemetry and hit Predict to activate the twin</div>
            </div>
          )}

          {correction && (
            <div className="result-panel amber fade-in">
              <div className="card-title" style={{ marginBottom: '1rem' }}>Corrective Setpoints</div>
              <div className="grid-2">
                {[
                  { label: 'ΔTemp', val: correction.delta_temp_c, unit: '°C', rec: `→ ${correction.recommended_temp_c}°C` },
                  { label: 'ΔCryst', val: correction.delta_crystallinity * 100, unit: '%', rec: `→ ${(correction.recommended_crystallinity * 100).toFixed(1)}%` },
                ].map(d => (
                  <div key={d.label}>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>{d.label}</div>
                    <div style={{ fontSize: '1.6rem', fontWeight: 800, fontFamily: 'var(--font-mono)', color: d.val >= 0 ? 'var(--accent-cyan)' : 'var(--accent-red)' }}>
                      {d.val >= 0 ? '+' : ''}{d.val.toFixed(1)}{d.unit}
                    </div>
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>{d.rec}</div>
                  </div>
                ))}
              </div>
              <div className="divider" />
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                <span className="badge badge-green">Projected: {correction.projected_eb.toFixed(1)} MV/m</span>
                <span className={`badge ${correction.projected_error < 30 ? 'badge-green' : 'badge-amber'}`}>±{correction.projected_error.toFixed(1)} MV/m</span>
              </div>
            </div>
          )}

          {history.length > 0 && (
            <div className="card fade-in">
              <div className="card-title" style={{ marginBottom: '0.75rem' }}>Telemetry Log</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', maxHeight: '240px', overflowY: 'auto' }}>
                {history.map((h, i) => (
                  <div key={i} style={{ display: 'grid', gridTemplateColumns: '70px 60px 90px 55px', gap: '0.5rem', fontSize: '0.72rem', fontFamily: 'var(--font-mono)', padding: '0.3rem 0.5rem', background: i === 0 ? 'var(--accent-cyan-dim)' : 'var(--bg-surface)', borderRadius: '6px', alignItems: 'center' }}>
                    <span style={{ color: 'var(--text-muted)' }}>{h.time}</span>
                    <span style={{ color: 'var(--accent-cyan)' }}>{h.temp.toFixed(0)}°C</span>
                    <span style={{ color: ebColor(h.eb), fontWeight: 700 }}>{h.eb.toFixed(1)} MV/m</span>
                    <span className={`badge badge-${h.good_fit ? 'green' : 'red'}`} style={{ fontSize: '0.62rem' }}>{h.good_fit ? 'OK' : 'LOW'}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
