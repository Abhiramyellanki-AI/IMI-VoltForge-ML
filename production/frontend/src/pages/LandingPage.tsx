import React from 'react';

interface LandingPageProps {
  onLaunch: () => void;
}

export default function LandingPage({ onLaunch }: LandingPageProps) {
  return (
    <div style={{ backgroundColor: 'var(--bg-base)', color: 'var(--text-primary)', minHeight: '100vh', fontFamily: 'var(--font-sans)', overflowX: 'hidden' }}>
      
      {/* LANDING NAVBAR */}
      <nav style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1.5rem 4rem', borderBottom: '1px solid var(--border-subtle)', background: 'rgba(10, 10, 10, 0.8)', backdropFilter: 'blur(12px)', position: 'fixed', width: '100%', zIndex: 100 }}>
        <div style={{ fontSize: '1.25rem', fontWeight: 600, letterSpacing: '-0.02em', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ width: 28, height: 28, background: 'var(--text-primary)', color: 'var(--bg-base)', borderRadius: 4, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1rem', fontWeight: 700 }}>V</div>
          VoltForge ML
        </div>
        <div style={{ display: 'flex', gap: '2.5rem', color: 'var(--text-secondary)', fontSize: '0.9rem', fontWeight: 500 }}>
          <a href="#features" style={{ color: 'inherit', textDecoration: 'none', transition: 'var(--transition)' }} onMouseOver={e => e.currentTarget.style.color = 'var(--text-primary)'} onMouseOut={e => e.currentTarget.style.color = 'var(--text-secondary)'}>Features</a>
          <a href="#architecture" style={{ color: 'inherit', textDecoration: 'none', transition: 'var(--transition)' }} onMouseOver={e => e.currentTarget.style.color = 'var(--text-primary)'} onMouseOut={e => e.currentTarget.style.color = 'var(--text-secondary)'}>Architecture</a>
          <a href="#analytics" style={{ color: 'inherit', textDecoration: 'none', transition: 'var(--transition)' }} onMouseOver={e => e.currentTarget.style.color = 'var(--text-primary)'} onMouseOut={e => e.currentTarget.style.color = 'var(--text-secondary)'}>Analytics</a>
          <a href="#research" style={{ color: 'inherit', textDecoration: 'none', transition: 'var(--transition)' }} onMouseOver={e => e.currentTarget.style.color = 'var(--text-primary)'} onMouseOut={e => e.currentTarget.style.color = 'var(--text-secondary)'}>Research</a>
        </div>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <button className="btn btn-amber" style={{ padding: '0.5rem 1.25rem' }} onClick={onLaunch}>Get Started</button>
        </div>
      </nav>

      {/* HERO SECTION */}
      <section style={{ paddingTop: '14rem', paddingBottom: '6rem', paddingLeft: '4rem', paddingRight: '4rem', textAlign: 'center', position: 'relative' }}>
        <div style={{ position: 'absolute', top: '10%', left: '50%', transform: 'translateX(-50%)', width: '60vw', height: '60vh', background: 'radial-gradient(circle, rgba(249, 115, 22, 0.08) 0%, transparent 60%)', zIndex: 0, pointerEvents: 'none' }} />
        
        <h1 style={{ fontSize: '5.5rem', fontWeight: 600, letterSpacing: '-0.04em', lineHeight: 1.1, marginBottom: '1.5rem', position: 'relative', zIndex: 1 }}>
          AI-Powered<br />Polymer Intelligence
        </h1>
        <p style={{ fontSize: '1.25rem', color: 'var(--text-secondary)', maxWidth: 800, margin: '0 auto 3rem auto', lineHeight: 1.6, position: 'relative', zIndex: 1 }}>
          Accelerate dielectric polymer discovery using machine learning, molecular embeddings, inverse design optimization, and computational chemistry pipelines.
        </p>
        <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', position: 'relative', zIndex: 1 }}>
          <button className="btn btn-amber" style={{ padding: '1rem 2rem', fontSize: '1.1rem' }} onClick={onLaunch}>Get Started</button>
          <a href="#architecture" className="btn btn-secondary" style={{ padding: '1rem 2rem', fontSize: '1.1rem', textDecoration: 'none' }}>View Architecture</a>
        </div>
        
        {/* Visual Mockup Area */}
        <div style={{ marginTop: '6rem', position: 'relative', zIndex: 1, display: 'flex', justifyContent: 'center' }}>
          <div style={{ width: '85%', maxWidth: 1100, height: 450, background: 'var(--bg-elevated)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-lg)', boxShadow: '0 24px 60px rgba(0,0,0,0.6)', position: 'relative', overflow: 'hidden' }}>
            <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 48, borderBottom: '1px solid var(--border-subtle)', background: 'var(--bg-surface)', display: 'flex', alignItems: 'center', padding: '0 1.25rem', gap: '0.5rem' }}>
              <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#EF4444' }} />
              <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#F59E0B' }} />
              <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#10B981' }} />
            </div>
            <div style={{ padding: '2rem', display: 'flex', height: '100%', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', paddingTop: '48px' }}>
               {/* Process-Structure-Property (PSP) Linkages SVG */}
               <svg width="100%" height="100%" viewBox="0 0 800 300" style={{ opacity: 0.9 }}>
                 {/* Connections (drawn underneath) */}
                 <line x1="200" y1="150" x2="400" y2="150" stroke="var(--accent-orange-dim)" strokeWidth="4" />
                 <line x1="400" y1="150" x2="600" y2="150" stroke="rgba(255,255,255,0.15)" strokeWidth="4" />
                 
                 {/* Process Node */}
                 <circle cx="200" cy="150" r="28" fill="var(--accent-orange)" />
                 <text x="200" y="210" fill="var(--text-primary)" fontSize="14" fontWeight="600" textAnchor="middle" letterSpacing="2">PROCESS</text>
                 <text x="200" y="235" fill="var(--text-secondary)" fontSize="12" textAnchor="middle">Synthesis Parameters</text>
                 
                 {/* Structure Node */}
                 <ellipse cx="400" cy="150" rx="55" ry="35" fill="#111111" stroke="rgba(255,255,255,0.1)" strokeWidth="2" />
                 <text x="400" y="210" fill="var(--text-primary)" fontSize="14" fontWeight="600" textAnchor="middle" letterSpacing="2">STRUCTURE</text>
                 <text x="400" y="235" fill="var(--text-secondary)" fontSize="12" textAnchor="middle">Molecular Embeddings</text>

                 {/* Property Node */}
                 <circle cx="600" cy="150" r="30" fill="#E5E5E5" />
                 <text x="600" y="210" fill="var(--text-primary)" fontSize="14" fontWeight="600" textAnchor="middle" letterSpacing="2">PROPERTY</text>
                 <text x="600" y="235" fill="var(--text-secondary)" fontSize="12" textAnchor="middle">Dielectric Strength</text>
               </svg>
            </div>
          </div>
        </div>
      </section>

      {/* TRUST / METRICS SECTION */}
      <section style={{ padding: '5rem 4rem', borderTop: '1px solid var(--border-subtle)', borderBottom: '1px solid var(--border-subtle)', background: 'var(--bg-surface)' }}>
        <div className="grid-3" style={{ maxWidth: 1200, margin: '0 auto', gap: '3rem' }}>
          {[
            { label: 'Polymer Architectures', value: '720' },
            { label: 'Feature Space', value: '2,128-Dim' },
            { label: 'Model Accuracy (R²)', value: '0.9319' },
            { label: 'Molecular Fingerprints', value: '1024-bit' },
            { label: 'Embeddings', value: 'PolyBERT' },
            { label: 'Optimization Pipeline', value: 'Real-Time' },
          ].map((m, i) => (
            <div key={i} style={{ padding: '1.5rem', borderLeft: '2px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '2.25rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.5rem', letterSpacing: '-0.02em' }}>{m.value}</div>
              <div style={{ fontSize: '0.95rem', color: 'var(--text-muted)' }}>{m.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* FEATURES SECTION */}
      <section id="features" style={{ padding: '8rem 4rem', maxWidth: 1200, margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: '5rem' }}>
          <h2 style={{ fontSize: '3rem', fontWeight: 600, marginBottom: '1rem', letterSpacing: '-0.03em' }}>Platform Features</h2>
          <p style={{ fontSize: '1.2rem', color: 'var(--text-secondary)', maxWidth: 600, margin: '0 auto' }}>End-to-end intelligent tools for advanced materials discovery.</p>
        </div>
        <div className="grid-3" style={{ gap: '2rem' }}>
          {[
            { title: 'Polymer Generation', desc: 'Automated combinatorial synthesis of PP, PET, and PVDF families with high-throughput architecture generation.' },
            { title: 'Molecular Intelligence', desc: 'Advanced extraction using RDKit descriptors, structural features, fingerprints, and Transformer embeddings.' },
            { title: 'AI Prediction Engine', desc: 'Ensemble machine learning, deep neural networks, and gradient boosting for Eb property prediction.' },
            { title: 'Inverse Design', desc: 'L-BFGS-B optimization for real-time target property matching via temperature and crystallinity tuning.' },
            { title: 'Digital Twin', desc: 'Live telemetry systems with sensor-based prediction loops and seamless hardware integration pipelines.' },
            { title: 'Analytics Dashboard', desc: 'Scientific visualization, ML metrics, feature-space analysis, and research-grade monitoring.' },
          ].map((f, i) => (
            <div key={i} className="card" style={{ padding: '2.5rem' }}>
              <div style={{ width: 48, height: 48, borderRadius: 'var(--radius-sm)', background: 'var(--accent-orange-dim)', color: 'var(--accent-orange)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '2rem', fontSize: '1.25rem', fontWeight: 600 }}>{i + 1}</div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '1rem', color: 'var(--text-primary)' }}>{f.title}</h3>
              <p style={{ fontSize: '0.95rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ARCHITECTURE SECTION */}
      <section id="architecture" style={{ padding: '8rem 4rem', background: 'var(--bg-surface)', borderTop: '1px solid var(--border-subtle)', borderBottom: '1px solid var(--border-subtle)' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto', textAlign: 'center' }}>
          <h2 style={{ fontSize: '3rem', fontWeight: 600, marginBottom: '5rem', letterSpacing: '-0.03em' }}>Zero-Leakage Pipeline Architecture</h2>
          
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1rem', overflowX: 'auto', paddingBottom: '2rem' }}>
            {['Polymer Generation', 'Feature Extraction', 'Molecular Embeddings', 'Feature Aggregation', 'ML Regression', 'Inverse Optimization', 'Prediction Output'].map((step, i, arr) => (
              <React.Fragment key={step}>
                <div style={{ flexShrink: 0, padding: '1.25rem 1.75rem', background: 'var(--bg-higher)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', fontSize: '0.9rem', fontWeight: 500, color: i === arr.length - 1 ? 'var(--accent-orange)' : 'var(--text-primary)', boxShadow: '0 4px 12px rgba(0,0,0,0.2)' }}>
                  {step}
                </div>
                {i < arr.length - 1 && (
                  <div style={{ flexShrink: 0, width: 40, height: 2, background: 'var(--border-subtle)' }} />
                )}
              </React.Fragment>
            ))}
          </div>
        </div>
      </section>

      {/* RESEARCH SECTION */}
      <section id="research" style={{ padding: '8rem 4rem', maxWidth: 1200, margin: '0 auto' }}>
        <div className="grid-2" style={{ alignItems: 'center', gap: '4rem' }}>
          <div>
            <h2 style={{ fontSize: '3rem', fontWeight: 600, marginBottom: '1.5rem', letterSpacing: '-0.03em' }}>Scientific Foundation</h2>
            <p style={{ fontSize: '1.1rem', color: 'var(--text-secondary)', marginBottom: '2.5rem', lineHeight: 1.6 }}>
              Built on robust computational chemistry and state-of-the-art machine learning. We combine traditional physical parameters with advanced deep learning embeddings to achieve unprecedented prediction accuracy.
            </p>
            <ul style={{ listStyle: 'none', padding: 0, display: 'grid', gap: '1.25rem' }}>
              {[
                '40 Structural Features',
                '40 Physical Parameters',
                '1024-bit Morgan Fingerprints',
                '600D PolyBERT Embeddings',
                'Ensemble ML Models',
                'Zero-leakage pipeline design'
              ].map(item => (
                <li key={item} style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '1.05rem', color: 'var(--text-primary)', fontWeight: 500 }}>
                  <span style={{ color: 'var(--accent-orange)', background: 'var(--accent-orange-dim)', width: 24, height: 24, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.8rem' }}>✓</span> {item}
                </li>
              ))}
            </ul>
          </div>
          <div className="card" style={{ background: 'var(--bg-surface)', height: 450, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div style={{ textAlign: 'center', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
              [ Feature Space Visualization ]<br/><br/>
              PCA / UMAP Projection
            </div>
          </div>
        </div>
      </section>

      {/* DASHBOARD PREVIEW */}
      <section id="analytics" style={{ padding: '8rem 4rem', background: 'var(--bg-surface)', borderTop: '1px solid var(--border-subtle)' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto', textAlign: 'center' }}>
          <h2 style={{ fontSize: '3rem', fontWeight: 600, marginBottom: '1rem', letterSpacing: '-0.03em' }}>Enterprise Analytics Console</h2>
          <p style={{ fontSize: '1.2rem', color: 'var(--text-secondary)', marginBottom: '5rem' }}>Analytics, Inverse Design, Digital Twin, and Feature Space all in one place.</p>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
            <div className="card" style={{ height: 350, display: 'flex', flexDirection: 'column', alignItems: 'flex-start', justifyContent: 'flex-end', padding: '2.5rem', textAlign: 'left', background: 'linear-gradient(135deg, var(--bg-elevated) 0%, rgba(249,115,22,0.08) 100%)' }}>
              <div style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '0.5rem', color: 'var(--text-primary)' }}>Inverse Design Console</div>
              <div style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>Real-time L-BFGS-B parameter tuning.</div>
            </div>
            <div className="card" style={{ height: 350, display: 'flex', flexDirection: 'column', alignItems: 'flex-start', justifyContent: 'flex-end', padding: '2.5rem', textAlign: 'left', background: 'linear-gradient(135deg, var(--bg-elevated) 0%, rgba(16,185,129,0.08) 100%)' }}>
              <div style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '0.5rem', color: 'var(--text-primary)' }}>Digital Twin System</div>
              <div style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>Hardware-in-the-loop IoT telemetry.</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA SECTION */}
      <section style={{ padding: '10rem 4rem', textAlign: 'center', background: 'var(--bg-base)', borderTop: '1px solid var(--border-subtle)' }}>
        <h2 style={{ fontSize: '4rem', fontWeight: 600, letterSpacing: '-0.04em', marginBottom: '1.5rem', lineHeight: 1.1 }}>Start Designing Next-Generation<br />Dielectric Materials</h2>
        <p style={{ fontSize: '1.25rem', color: 'var(--text-secondary)', marginBottom: '4rem', maxWidth: 600, margin: '0 auto 4rem auto' }}>
          From molecular embeddings to inverse optimization — all in one intelligent platform.
        </p>
        <button className="btn btn-amber" style={{ padding: '1.25rem 3rem', fontSize: '1.1rem' }} onClick={onLaunch}>Launch Dashboard</button>
      </section>

      {/* FOOTER */}
      <footer style={{ padding: '4rem', background: 'var(--bg-surface)', borderTop: '1px solid var(--border-subtle)' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '2rem' }}>
          <div>
            <div style={{ fontSize: '1.25rem', fontWeight: 600, letterSpacing: '-0.02em', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem', color: 'var(--text-primary)' }}>
              <div style={{ width: 24, height: 24, background: 'var(--text-primary)', color: 'var(--bg-base)', borderRadius: 4, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.85rem' }}>V</div>
              VoltForge ML
            </div>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>© 2026 VoltForge ML. All rights reserved.</div>
          </div>
          <div style={{ display: 'flex', gap: '5rem' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', fontSize: '0.95rem' }}>
              <div style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.5rem' }}>Product</div>
              <a href="#" style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>Research Platform</a>
              <a href="#" style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>Documentation</a>
              <a href="#" style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>Analytics</a>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', fontSize: '0.95rem' }}>
              <div style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.5rem' }}>Company</div>
              <a href="#" style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>GitHub</a>
              <a href="#" style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>Contact</a>
              <a href="#" style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>Privacy</a>
              <a href="#" style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>Terms</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
