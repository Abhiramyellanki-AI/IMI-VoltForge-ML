interface NavbarProps {
  activePage: string;
  onNavigate: (page: string) => void;
}

const navItems = [
  { id: 'dashboard', icon: '⬡', label: 'Dashboard' },
  { id: 'inverse',   icon: '⟳', label: 'Inverse Design' },
  { id: 'search',    icon: '◈', label: 'Polymer Search' },
  { id: 'twin',      icon: '◎', label: 'Digital Twin' },
  { id: 'hardware',  icon: '⚙', label: 'Hardware I/O' },
];

export default function Navbar({ activePage, onNavigate }: NavbarProps) {
  return (
    <nav className="navbar">
      <div className="navbar-logo">
        <div className="navbar-logo-icon">V</div>
        VoltForge ML
      </div>

      <span className="nav-section-label">Analysis</span>
      {navItems.slice(0, 2).map(item => (
        <button
          key={item.id}
          className={`nav-link ${activePage === item.id ? 'active' : ''}`}
          onClick={() => onNavigate(item.id)}
        >
          <span className="nav-icon">{item.icon}</span>
          {item.label}
        </button>
      ))}

      <span className="nav-section-label">Generation</span>
      <button
        className={`nav-link ${activePage === 'search' ? 'active' : ''}`}
        onClick={() => onNavigate('search')}
      >
        <span className="nav-icon">◈</span>
        Polymer Search
      </button>
      <button
        className={`nav-link ${activePage === 'generative' ? 'active' : ''}`}
        onClick={() => onNavigate('generative')}
      >
        <span className="nav-icon">🧬</span>
        De Novo Generation
      </button>

      <span className="nav-section-label">Live Systems</span>
      {navItems.slice(3).map(item => (
        <button
          key={item.id}
          className={`nav-link ${activePage === item.id ? 'active' : ''}`}
          onClick={() => onNavigate(item.id)}
        >
          <span className="nav-icon">{item.icon}</span>
          {item.label}
        </button>
      ))}

      <div className="navbar-footer">
        <p className="navbar-footer-text">VoltForge ML Platform</p>
        <p className="navbar-footer-text" style={{ color: 'var(--accent-orange)', marginTop: '2px' }}>
          Phase 2 — Production
        </p>
      </div>
    </nav>
  );
}
