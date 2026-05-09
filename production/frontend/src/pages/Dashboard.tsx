import { useEffect, useState } from 'react';
import { api, type HealthResponse } from '../api/client';

const METRICS = [
  { label: 'Architecture',   value: '9-File Pipeline',    unit: '',      color: 'cyan'  },
  { label: 'Polymers',       value: '720',                unit: 'SMILES', color: 'amber' },
  { label: 'Feature Space',  value: '2,128',              unit: 'dims',   color: 'cyan'  },
  { label: 'Baseline R²',    value: '0.9319',             unit: '',       color: 'amber' },
  { label: 'Baseline MAE',   value: '12.45',              unit: 'MV/m',   color: 'cyan'  },
  { label: 'Optimizer',      value: 'L-BFGS-B',          unit: '',       color: 'amber' },
];

const MODEL_PIPELINE = [
  'Morgan PCA (1024→256)',
  'PolyBERT PCA (600→128)',
  'Structural (40)',
  'Physical (40)',
  'SimpleImputer',
  'StandardScaler',
  'CollinearityDropper',
  'MLP (128,64)',
  '+ GBR Ensemble',
];

export default function Dashboard() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api.health()
      .then(setHealth)
      .catch(() => setError('API offline — start the FastAPI backend first.'))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="fade-in">
      <div className="page-header">
        <h1 className="page-title">Polymer Informatics Dashboard</h1>
        <p className="page-subtitle">
          Materials Informatics pipeline for inverse design of high-performance dielectric polymers (E<sub>b</sub>)
        </p>
      </div>

      {/* API Status */}
      <div className="section">
        <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '1rem', padding: '1rem 1.5rem' }}>
          {loading ? (
            <><span className="spinner" /> <span style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Connecting to API...</span></>
          ) : error ? (
            <><span className="status-dot offline" /> <span style={{ color: 'var(--accent-red)', fontSize: '0.875rem' }}>{error}</span></>
          ) : (
            <>
              <span className="status-dot online" />
              <span style={{ fontSize: '0.875rem', color: 'var(--text-primary)', fontWeight: 600 }}>API Online</span>
              <span className="badge badge-cyan" style={{ marginLeft: 'auto' }}>
                {health?.ensemble_loaded ? 'Ensemble Model' : 'MLP Model'} Active
              </span>
              <span className="badge badge-green">{health?.dataset_rows ?? 0} Polymers Loaded</span>
            </>
          )}
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div className="section">
        <h2 className="section-title">⬡ System Metrics</h2>
        <div className="grid-3">
          {METRICS.map((m) => (
            <div key={m.label} className="card">
              <div className="card-title">{m.label}</div>
              <div className="card-value" style={{ color: m.color === 'cyan' ? 'var(--accent-cyan)' : 'var(--accent-amber)' }}>
                {m.value}
                {m.unit && <span className="card-unit">{m.unit}</span>}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Pipeline Architecture */}
      <div className="section">
        <h2 className="section-title">◎ Model Pipeline (Phase A)</h2>
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
            {MODEL_PIPELINE.map((step, i) => (
              <>
                <span key={step} className="badge" style={{
                  background: step.startsWith('+') ? 'var(--accent-amber-dim)' : 'var(--accent-cyan-dim)',
                  color: step.startsWith('+') ? 'var(--accent-amber)' : 'var(--accent-cyan)',
                  border: `1px solid ${step.startsWith('+') ? 'rgba(255,184,48,0.25)' : 'rgba(0,212,255,0.25)'}`,
                  fontFamily: 'var(--font-mono)',
                  fontSize: '0.7rem'
                }}>
                  {step}
                </span>
                {i < MODEL_PIPELINE.length - 1 && (
                  <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>→</span>
                )}
              </>
            ))}
          </div>
          <div className="divider" />
          <div className="grid-3">
            <div>
              <div className="card-title">Polymer Classes</div>
              <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap', marginTop: '0.3rem' }}>
                {['PP', 'PET', 'PVDF'].map(cls => (
                  <span key={cls} className="badge badge-amber">{cls}</span>
                ))}
              </div>
            </div>
            <div>
              <div className="card-title">Optimizer</div>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem', color: 'var(--accent-cyan)', marginTop: '0.3rem' }}>
                SciPy L-BFGS-B<br />
                <span style={{ color: 'var(--text-secondary)', fontSize: '0.75rem' }}>
                  Bounds: Temp [100,300]°C · Cryst [0.1,0.9]
                </span>
              </div>
            </div>
            <div>
              <div className="card-title">Target Property</div>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem', color: 'var(--accent-amber)', marginTop: '0.3rem' }}>
                E<sub>b</sub> (MV/m)<br />
                <span style={{ color: 'var(--text-secondary)', fontSize: '0.75rem' }}>
                  Good Fit threshold: ≥ 450 MV/m
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Phase 2 Features */}
      <div className="section">
        <h2 className="section-title">◈ Phase 2 Features Available</h2>
        <div className="grid-2">
          {[
            { icon: '⟳', title: 'Inverse Design', desc: 'L-BFGS-B optimization of Temperature + Crystallinity toward a target Eb', page: 'inverse' },
            { icon: '◈', title: 'Polymer Search', desc: 'Similarity-ranked candidate retrieval by Eb target + polymer class', page: 'search' },
            { icon: '◎', title: 'Digital Twin', desc: 'Real-time telemetry → Eb prediction with correction loop feedback', page: 'twin' },
            { icon: '⚙', title: 'Hardware I/O', desc: 'IoT bridge simulation: sensor read → predict → setpoint write loop', page: 'hardware' },
          ].map(f => (
            <div key={f.title} className="card" style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
              <div style={{ fontSize: '1.5rem', color: 'var(--accent-cyan)', flexShrink: 0 }}>{f.icon}</div>
              <div>
                <div style={{ fontWeight: 700, color: 'var(--text-primary)', marginBottom: '0.25rem' }}>{f.title}</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{f.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
