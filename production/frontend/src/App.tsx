import { useState } from 'react';
import './index.css';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import InverseDesign from './pages/InverseDesign';
import ConditionalSearch from './pages/ConditionalSearch';
import GenerativeDesign from './pages/GenerativeDesign';
import DigitalTwin from './pages/DigitalTwin';
import HardwareMonitor from './pages/HardwareMonitor';
import LandingPage from './pages/LandingPage';

type Page = 'landing' | 'dashboard' | 'inverse' | 'search' | 'generative' | 'twin' | 'hardware';

function App() {
  const [activePage, setActivePage] = useState<Page>('landing');

  if (activePage === 'landing') {
    return <LandingPage onLaunch={() => setActivePage('dashboard')} />;
  }

  const renderPage = () => {
    switch (activePage) {
      case 'dashboard': return <Dashboard />;
      case 'inverse':   return <InverseDesign />;
      case 'search':    return <ConditionalSearch />;
      case 'generative': return <GenerativeDesign />;
      case 'twin':      return <DigitalTwin />;
      case 'hardware':  return <HardwareMonitor />;
    }
  };

  return (
    <div className="app-shell">
      <Navbar activePage={activePage} onNavigate={(p) => setActivePage(p as Page)} />
      <main className="main-content">
        {renderPage()}
      </main>
    </div>
  );
}

export default App;
