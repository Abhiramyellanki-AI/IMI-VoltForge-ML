import { useState } from 'react';
import { api, type CandidatePolymer, type ConditionalSearchResponse } from '../api/client';

const POLYMER_CLASSES = ['PVDF', 'PET', 'PP'];

export default function ConditionalSearch() {
  const [targetEb,      setTargetEb]      = useState(600);
  const [polymerClass,  setPolymerClass]  = useState('PVDF');
  const [topK,          setTopK]          = useState(5);
  const [loading,       setLoading]       = useState(false);
  const [result,        setResult]        = useState<ConditionalSearchResponse | null>(null);
  const [error,         setError]         = useState('');

  const run = async () => {
    setLoading(true); setError(''); setResult(null);
    try {
      const res = await api.conditionalSearch({ target_eb: targetEb, polymer_class: polymerClass, top_k: topK });
      setResult(res);
    } catch (e: any) {
      setError(e.message ?? 'Request failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fade-in">
      <div className="page-header">
        <h1 className="page-title">◈ Conditional Polymer Search</h1>
        <p className="page-subtitle">
          Input a target E<sub>b</sub> and polymer family — the engine retrieves the closest
          matches, then re-ranks for structural diversity in Morgan fingerprint space.
        </p>
      </div>

      {/* Search Form */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div className="grid-3" style={{ gap: '1.5rem', alignItems: 'end' }}>
          <div className="form-group">
            <label className="form-label">Target E<sub>b</sub> (MV/m)</label>
            <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
              <input
                id="search-target-eb"
                type="range"
                className="range-slider"
                min={200} max={800} step={10}
                value={targetEb}
                onChange={e => setTargetEb(Number(e.target.value))}
              />
              <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-cyan)', minWidth: '65px', fontWeight: 700 }}>
                {targetEb}
              </span>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Polymer Class</label>
            <select
              id="search-polymer-class"
              className="form-select"
              value={polymerClass}
              onChange={e => setPolymerClass(e.target.value)}
            >
              {POLYMER_CLASSES.map(c => <option key={c}>{c}</option>)}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Top K Candidates</label>
            <input
              id="search-top-k"
              type="number"
              className="form-input"
              value={topK} min={1} max={20}
              onChange={e => setTopK(Number(e.target.value))}
            />
          </div>
        </div>

        <div style={{ marginTop: '1.25rem', display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <button id="search-run-btn" className="btn btn-primary" onClick={run} disabled={loading}>
            {loading ? <><span className="spinner" /> Searching...</> : '◈ Search Polymers'}
          </button>
          {result && (
            <span className="badge badge-green">
              {result.total_found} candidates found for {result.query_polymer_class} @ {result.query_target_eb} MV/m
            </span>
          )}
        </div>

        {error && <div className="error-banner" style={{ marginTop: '1rem' }}><span>⚠</span> {error}</div>}
      </div>

      {/* Algorithm explanation */}
      <div className="card" style={{ marginBottom: '1.5rem', background: 'var(--accent-cyan-dim)', border: '1px solid var(--border-active)' }}>
        <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
          {[
            { step: '1', label: 'Class Filter', desc: 'SMILES pattern → PP / PET / PVDF' },
            { step: '2', label: 'Eb Proximity', desc: 'Rank by |Target_Eb − query_eb|' },
            { step: '3', label: 'Top-20 Pool', desc: 'Pre-filter to 20 closest matches' },
            { step: '4', label: 'Diversity Re-rank', desc: 'Greedy max-min Morgan cosine distance' },
            { step: '5', label: 'Return Top-K', desc: 'Structurally diverse final candidates' },
          ].map(s => (
            <div key={s.step} style={{ display: 'flex', gap: '0.6rem', alignItems: 'flex-start', minWidth: '150px' }}>
              <div style={{ width: '22px', height: '22px', borderRadius: '50%', background: 'var(--accent-cyan)', color: 'var(--bg-base)', fontWeight: 800, fontSize: '0.72rem', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                {s.step}
              </div>
              <div>
                <div style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--accent-cyan)' }}>{s.label}</div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>{s.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Results */}
      {result && result.candidates.length > 0 && (
        <div className="section fade-in">
          <h2 className="section-title">◈ Candidate Polymers</h2>
          <div className="grid-1" style={{ gap: '0.75rem' }}>
            {result.candidates.map((c: CandidatePolymer) => (
              <div key={c.rank} className="molecule-card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <div className="molecule-rank">#{c.rank} — {c.polymer_class}</div>
                  <div style={{ display: 'flex', gap: '0.4rem' }}>
                    <span className="badge badge-cyan">E<sub>b</sub> = {c.target_eb_dataset} MV/m</span>
                    <span className={`badge ${c.eb_delta < 20 ? 'badge-green' : c.eb_delta < 80 ? 'badge-amber' : 'badge-red'}`}>
                      Δ {c.eb_delta} MV/m
                    </span>
                  </div>
                </div>
                <div className="molecule-smiles">{c.smiles}</div>
                <div className="molecule-stats">
                  <div className="molecule-stat">
                    <div className="molecule-stat-value">{c.processing_temp_c}°C</div>
                    <div className="molecule-stat-label">Temp</div>
                  </div>
                  <div className="molecule-stat">
                    <div className="molecule-stat-value">{(c.crystallinity * 100).toFixed(1)}%</div>
                    <div className="molecule-stat-label">Crystallinity</div>
                  </div>
                  <div className="molecule-stat">
                    <div className="molecule-stat-value">{c.target_eb_dataset >= 450 ? '✓' : '✕'}</div>
                    <div className="molecule-stat-label">Good Fit</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
