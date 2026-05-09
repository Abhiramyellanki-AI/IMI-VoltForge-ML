import { useState } from 'react';
import { api, type InverseDesignResponse } from '../api/client';

const DEFAULT_SMILES = 'CC(F)(C(F)(F)F)CC(F)(I)';

export default function InverseDesign() {
  const [smiles,    setSmiles]    = useState(DEFAULT_SMILES);
  const [targetEb,  setTargetEb]  = useState(700);
  const [maxIter,   setMaxIter]   = useState(500);
  const [loading,   setLoading]   = useState(false);
  const [result,    setResult]    = useState<InverseDesignResponse | null>(null);
  const [error,     setError]     = useState('');

  const run = async () => {
    setLoading(true); setError(''); setResult(null);
    try {
      const res = await api.inverseDesign({ smiles, target_eb: targetEb, max_iter: maxIter });
      setResult(res);
    } catch (e: any) {
      setError(e.message ?? 'Request failed');
    } finally {
      setLoading(false);
    }
  };

  const errorPct = result?.absolute_error != null && result.target_eb > 0
    ? ((result.absolute_error / result.target_eb) * 100).toFixed(1)
    : null;

  return (
    <div className="fade-in">
      <div className="page-header">
        <h1 className="page-title">⟳ Inverse Design Optimizer</h1>
        <p className="page-subtitle">
          Freeze a polymer's molecular features, then let L-BFGS-B find the optimal
          ProcessingTemp + Crystallinity to hit your target E<sub>b</sub>.
        </p>
      </div>

      <div className="grid-2" style={{ alignItems: 'start' }}>
        {/* Input Panel */}
        <div className="card">
          <h2 className="section-title">Configuration</h2>

          <div className="section" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div className="form-group">
              <label className="form-label">Polymer SMILES</label>
              <input
                id="inverse-smiles"
                className="form-input mono"
                value={smiles}
                onChange={e => setSmiles(e.target.value)}
                placeholder="e.g. CC(F)(C(F)(F)F)CC(F)(I)"
              />
              <span className="form-hint">Lightweight RDKit features (no PolyBERT) — instant inference</span>
            </div>

            <div className="form-group">
              <label className="form-label">Target E<sub>b</sub> (MV/m)</label>
              <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                <input
                  id="inverse-target-eb"
                  type="range"
                  className="range-slider"
                  min={200} max={800} step={10}
                  value={targetEb}
                  onChange={e => setTargetEb(Number(e.target.value))}
                />
                <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-cyan)', minWidth: '65px', fontWeight: 700 }}>
                  {targetEb} MV/m
                </span>
              </div>
              <span className="form-hint">Training range: 200–800 MV/m</span>
            </div>

            <div className="form-group">
              <label className="form-label">Max Optimizer Iterations</label>
              <input
                id="inverse-max-iter"
                type="number"
                className="form-input"
                value={maxIter}
                min={50} max={5000}
                onChange={e => setMaxIter(Number(e.target.value))}
              />
            </div>

            <button id="inverse-run-btn" className="btn btn-primary btn-full" onClick={run} disabled={loading || !smiles}>
              {loading ? <><span className="spinner" /> Optimizing...</> : '⟳ Run L-BFGS-B Optimizer'}
            </button>

            {error && (
              <div className="error-banner">
                <span>⚠</span> {error}
              </div>
            )}
          </div>

          {/* Optimization bounds info */}
          <div className="divider" />
          <div className="card-title">Search Space</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginTop: '0.5rem' }}>
            {[
              { label: 'ProcessingTemp_C', min: 100, max: 300, unit: '°C' },
              { label: 'Crystallinity',    min: 0.10, max: 0.90, unit: '' },
            ].map(b => (
              <div key={b.label}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.3rem' }}>
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{b.label}</span>
                  <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>[{b.min}{b.unit} → {b.max}{b.unit}]</span>
                </div>
                <div className="gauge-track"><div className="gauge-fill cyan" style={{ width: '100%' }} /></div>
              </div>
            ))}
          </div>
        </div>

        {/* Result Panel */}
        <div>
          {result ? (
            <div className={`result-panel ${!result.success ? 'amber' : ''}`}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
                <span className="card-title">Optimization Result</span>
                <span className={`badge ${result.success ? 'badge-green' : 'badge-red'}`}>
                  {result.success ? '✓ Converged' : '✕ Not Converged'}
                </span>
              </div>

              {result.success && result.predicted_eb != null ? (
                <>
                  <div style={{ marginBottom: '1.25rem' }}>
                    <div className="card-title">Predicted E<sub>b</sub></div>
                    <div className="result-eb">{result.predicted_eb.toFixed(1)}<span className="result-unit"> MV/m</span></div>
                    <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem', flexWrap: 'wrap' }}>
                      <span className="badge badge-cyan">Target: {result.target_eb} MV/m</span>
                      <span className={`badge ${result.absolute_error! < 50 ? 'badge-green' : result.absolute_error! < 150 ? 'badge-amber' : 'badge-red'}`}>
                        Error: {result.absolute_error?.toFixed(1)} MV/m ({errorPct}%)
                      </span>
                      <span className="badge badge-cyan">{result.model_used}</span>
                    </div>
                  </div>

                  <div className="divider" />

                  <div className="grid-2" style={{ gap: '1rem' }}>
                    <div>
                      <div className="card-title">Optimal Temperature</div>
                      <div style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)' }}>
                        {result.optimal_temp_c?.toFixed(1)}°C
                      </div>
                      <div className="gauge-track" style={{ marginTop: '0.5rem' }}>
                        <div className="gauge-fill cyan" style={{ width: `${((result.optimal_temp_c! - 100) / 200) * 100}%` }} />
                      </div>
                    </div>
                    <div>
                      <div className="card-title">Optimal Crystallinity</div>
                      <div style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--accent-amber)', fontFamily: 'var(--font-mono)' }}>
                        {(result.optimal_crystallinity! * 100).toFixed(1)}%
                      </div>
                      <div className="gauge-track" style={{ marginTop: '0.5rem' }}>
                        <div className="gauge-fill amber" style={{ width: `${((result.optimal_crystallinity! - 0.1) / 0.8) * 100}%` }} />
                      </div>
                    </div>
                  </div>

                  <div className="divider" />
                  <div className="card-title">Polymer</div>
                  <div className="code-block">{result.smiles}</div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.5rem', fontFamily: 'var(--font-mono)' }}>
                    {result.optimizer_message}
                  </div>
                </>
              ) : (
                <div style={{ color: 'var(--accent-amber)', fontSize: '0.875rem' }}>
                  {result.optimizer_message}
                </div>
              )}
            </div>
          ) : (
            <div className="card" style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⟳</div>
              <div style={{ fontSize: '0.9rem' }}>Configure parameters and run the optimizer to see results</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
