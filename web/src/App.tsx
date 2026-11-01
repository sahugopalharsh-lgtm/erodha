import React, { useState, useEffect } from 'react';
import { PageId } from './types';
import { Navbar } from './components/layout/Navbar';
import { Footer } from './components/layout/Footer';
import { LandingPage } from './pages/LandingPage';
import { DashboardPage } from './pages/DashboardPage';
import { StockAnalysisPage } from './pages/StockAnalysisPage';
import { ForecastingPage } from './pages/ForecastingPage';
import { RiskAnalysisPage } from './pages/RiskAnalysisPage';
import { IpoAnalysisPage } from './pages/IpoAnalysisPage';
import { JumpDiffusionPage } from './pages/JumpDiffusionPage';
import { AboutPage } from './pages/AboutPage';
import { AnimatePresence, motion } from 'framer-motion';

export function App() {
  const [activePage, setActivePage] = useState<PageId>('landing');
  const [selectedSymbol, setSelectedSymbol] = useState<string>('RELIANCE');

  // Scroll to top on page change
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [activePage]);

  const renderPage = () => {
    switch (activePage) {
      case 'landing':
        return <LandingPage onNavigate={setActivePage} />;
      case 'dashboard':
        return (
          <DashboardPage
            selectedSymbol={selectedSymbol}
            onSelectStock={setSelectedSymbol}
            onNavigate={setActivePage}
          />
        );
      case 'stocks':
        return (
          <StockAnalysisPage
            selectedSymbol={selectedSymbol}
            onSelectStock={setSelectedSymbol}
          />
        );
      case 'forecast':
        return (
          <ForecastingPage
            selectedSymbol={selectedSymbol}
            onSelectStock={setSelectedSymbol}
          />
        );
      case 'risk':
        return (
          <RiskAnalysisPage
            selectedSymbol={selectedSymbol}
            onSelectStock={setSelectedSymbol}
          />
        );
      case 'ipo':
        return <IpoAnalysisPage />;
      case 'model':
        return <JumpDiffusionPage />;
      case 'about':
        return <AboutPage onNavigate={setActivePage} />;
      default:
        return <LandingPage onNavigate={setActivePage} />;
    }
  };

  return (
    <div className="min-h-screen bg-[#090a0f] text-slate-100 flex flex-col font-sans selection:bg-emerald-500/30 selection:text-emerald-300">
      {/* Navigation Header */}
      <Navbar
        activePage={activePage}
        onNavigate={setActivePage}
        selectedSymbol={selectedSymbol}
        onSelectStock={setSelectedSymbol}
      />

      {/* Main Content View with Framer Motion Page Transitions */}
      <main className="flex-grow">
        <AnimatePresence mode="wait">
          <motion.div
            key={activePage}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
          >
            {renderPage()}
          </motion.div>
        </AnimatePresence>
      </main>

      {/* Platform Footer */}
      <Footer onNavigate={setActivePage} />
    </div>
  );
}

export default App;
