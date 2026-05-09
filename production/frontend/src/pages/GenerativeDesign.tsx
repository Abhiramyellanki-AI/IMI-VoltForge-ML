import { useState } from 'react';
import { api, type GenerativeDesignResponse } from '../api/client';

export default function GenerativeDesign() {
  const [targetEb, setTargetEb] = useState<number>(650.0);
  const [generations, setGenerations] = useState<number>(10);
  const [popSize, setPopSize] = useState<number>(30);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<GenerativeDesignResponse | null>(null);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await api.generativeDesign({ target_eb: targetEb, generations, pop_size: popSize });
      setResult(res);
    } catch (err: any) {
      setError(err.message || 'An error occurred during generative design.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container fade-in">
      <header className="page-header">
        <div className="page-title-group">
          <h1 className="page-title">De Novo Generative Design</h1>
          <p className="page-subtitle">Synthesize novel polymers from scratch using Genetic Algorithms to hit target dielectric breakdown strengths.</p>
        </div>
      </header>

      <div className="grid" style={{ gridTemplateColumns: '1fr 2fr' }}>
        {/* Controls */}
        <div className="glass-panel">
          <h2 className="panel-title">Genetic Algorithm Config</h2>
          <form onSubmit={handleGenerate} className="form-group">
            <div className="form-row">
              <label className="form-label">Target Eb (MV/m)</label>
              <input
                type="number"
                step="10"
                required
                className="form-input"
                value={targetEb}
                onChange={(e) => setTargetEb(parseFloat(e.target.value))}
              />
            </div>
            
            <div className="form-row">
              <label className="form-label">Generations</label>
              <input
                type="number"
                min="1"
                max="50"
                required
                className="form-input"
                value={generations}
                onChange={(e) => setGenerations(parseInt(e.target.value))}
              />
            </div>

            <div className="form-row">
              <label className="form-label">Population Size</label>
              <input
                type="number"
                min="10"
                max="200"
                required
                className="form-input"
                value={popSize}
                onChange={(e) => setPopSize(parseInt(e.target.value))}
              />
            </div>

            <button type="submit" className="btn btn-primary w-full" disabled={loading} style={{ marginTop: '1rem' }}>
              {loading ? <span className="pulse">Evolving Population...</span> : 'Synthesize Polymer'}
            </button>
          </form>

          {error && (
            <div style={{ marginTop: '1rem', color: 'var(--danger)', fontSize: '0.875rem' }}>
              <strong>Error:</strong> {error}
            </div>
          )}
        </div>

        {/* Results */}
        <div className="glass-panel">
          <h2 className="panel-title">Evolutionary Output</h2>
          
          {!result && !loading && (
            <div style={{ textAlign: 'center', color: 'var(--text-dim)', padding: '2rem 0' }}>
              <div style={{ fontSize: '3rem', marginBottom: '1rem', opacity: 0.5 }}>🧬</div>
              <p>Configure parameters and click Synthesize to generate a novel polymer.</p>
            </div>
          )}

          {loading && (
            <div style={{ textAlign: 'center', padding: '2rem 0' }}>
              <div className="pulse" style={{ fontSize: '2rem', marginBottom: '1rem' }}>⟳</div>
              <p className="highlight">Running genetic crossover and mutation sequences...</p>
              <p style={{ color: 'var(--text-dim)', fontSize: '0.85rem', marginTop: '0.5rem' }}>This may take a moment depending on generation count.</p>
            </div>
          )}

          {result && (
            <div className="result-card fade-in">
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
                <div className="metric-box">
                  <span className="metric-label">Target Eb</span>
                  <span className="metric-value">{result.target_eb.toFixed(2)}</span>
                  <span className="metric-unit">MV/m</span>
                </div>
                <div className="metric-box" style={{ borderColor: 'var(--accent-cyan)' }}>
                  <span className="metric-label">Predicted Eb</span>
                  <span className="metric-value highlight">{result.predicted_eb.toFixed(2)}</span>
                  <span className="metric-unit">MV/m</span>
                </div>
                <div className="metric-box">
                  <span className="metric-label">Abs Error</span>
                  <span className="metric-value">{result.absolute_error.toFixed(2)}</span>
                  <span className="metric-unit">MV/m</span>
                </div>
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <span className="metric-label">Best Novel SMILES</span>
                <div className="terminal-box" style={{ marginTop: '0.5rem', wordBreak: 'break-all' }}>
                  {result.best_smiles}
                </div>
              </div>
              
              <div style={{ color: 'var(--text-dim)', fontSize: '0.85rem' }}>
                Generations required to converge: <strong>{result.generations_run}</strong> / {generations}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
