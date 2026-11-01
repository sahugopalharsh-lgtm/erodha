import React, { useState } from 'react';
import { PageId } from '../../types';
import { StockSelector } from '../ui/StockSelector';
import { useBackendStatus } from '../../hooks/useApi';
import {
  Activity,
  BarChart3,
  TrendingUp,
  ShieldAlert,
  Cpu,
  Info,
  Search,
  Menu,
  X,
  Sparkles,
  Layers,
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface NavbarProps {
  activePage: PageId;
  onNavigate: (page: PageId) => void;
  selectedSymbol: string;
  onSelectStock: (symbol: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  activePage,
  onNavigate,
  selectedSymbol,
  onSelectStock,
}) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const { isLive, health, checking, refresh } = useBackendStatus();

  const navItems: { id: PageId; label: string; icon: React.ReactNode }[] = [
    { id: 'landing', label: 'Home', icon: <Sparkles className="w-3.5 h-3.5" /> },
    { id: 'dashboard', label: 'Overview', icon: <BarChart3 className="w-3.5 h-3.5" /> },
    { id: 'stocks', label: 'Stocks', icon: <Activity className="w-3.5 h-3.5" /> },
    { id: 'forecast', label: 'Forecast', icon: <TrendingUp className="w-3.5 h-3.5" /> },
    { id: 'risk', label: 'Risk', icon: <ShieldAlert className="w-3.5 h-3.5" /> },
    { id: 'ipo', label: 'IPO Analyzer', icon: <Layers className="w-3.5 h-3.5" /> },
    { id: 'model', label: 'Model', icon: <Cpu className="w-3.5 h-3.5" /> },
    { id: 'about', label: 'About', icon: <Info className="w-3.5 h-3.5" /> },
  ];

  return (
    <header className="sticky top-0 z-50 bg-[#090a0f]/90 backdrop-blur-xl border-b border-white/10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Left: Brand Logo */}
          <div className="flex items-center gap-6">
            <button
              onClick={() => onNavigate('landing')}
              className="flex items-center gap-2.5 text-left group cursor-pointer"
            >
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-400 via-emerald-500 to-teal-700 flex items-center justify-center shadow-[0_0_20px_rgba(16,185,129,0.4)] group-hover:scale-105 transition-transform">
                <span className="font-mono font-black text-slate-950 text-base tracking-tighter">
                  ∑
                </span>
              </div>
              <div>
                <span className="font-extrabold text-slate-100 text-lg tracking-tight group-hover:text-emerald-400 transition-colors">
                  ERODHA
                </span>
                <span className="text-[9px] font-mono text-emerald-400 block tracking-widest uppercase -mt-1 font-semibold">
                  JUMP-DIFFUSION
                </span>
              </div>
            </button>

            {/* Desktop Navigation Links */}
            <nav className="hidden md:flex items-center gap-1 bg-slate-900/60 p-1 rounded-xl border border-white/5">
              {navItems.map((item) => {
                const isActive = activePage === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => onNavigate(item.id)}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                      isActive
                        ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 shadow-sm'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-white/5 border border-transparent'
                    }`}
                  >
                    {item.icon}
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Right Controls: Stock Selector, Search, Mobile Menu Toggle */}
          <div className="flex items-center gap-3">
            {/* Backend connectivity badge */}
            {isLive ? (
              <div
                title={`FastAPI backend live at port 8000 | Provider: ${health?.activeDataProvider || 'yfinance'}`}
                className="hidden xl:flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/25 text-[11px] font-mono text-emerald-400"
              >
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                <span>Backend Connected</span>
              </div>
            ) : (
              <button
                onClick={refresh}
                title="Backend is currently offline or unreachable. Click to re-connect."
                className="hidden xl:flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-amber-500/10 border border-amber-500/20 text-[11px] font-mono text-amber-300 hover:bg-amber-500/20 cursor-pointer transition-colors"
              >
                <span className={`w-1.5 h-1.5 rounded-full bg-amber-400 ${checking ? 'animate-ping' : ''}`} />
                <span>{checking ? 'Checking...' : 'Simulation Mode'}</span>
              </button>
            )}

            {/* Stock selector visible on desktop & tablet */}
            <div className="hidden sm:block">
              <StockSelector
                selectedSymbol={selectedSymbol}
                onSelectStock={onSelectStock}
              />
            </div>

            {/* Quick Search */}
            <div className="relative">
              {searchOpen ? (
                <div className="flex items-center bg-slate-900 border border-white/20 rounded-xl px-3 py-1.5 text-xs text-slate-200 shadow-xl">
                  <Search className="w-3.5 h-3.5 text-slate-400 mr-2" />
                  <input
                    type="text"
                    placeholder="Search RELIANCE, TCS, INFY..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    autoFocus
                    className="bg-transparent outline-none w-36 sm:w-48 text-xs text-slate-100 placeholder-slate-500"
                  />
                  <button onClick={() => setSearchOpen(false)} className="ml-1 text-slate-400 hover:text-slate-200">
                    <X className="w-3.5 h-3.5" />
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => setSearchOpen(true)}
                  className="p-2 rounded-xl bg-slate-900/80 hover:bg-slate-800 text-slate-400 hover:text-slate-200 border border-white/10 transition-colors cursor-pointer"
                  title="Search stock"
                >
                  <Search className="w-4 h-4" />
                </button>
              )}
            </div>

            {/* CTA Button */}
            <button
              onClick={() => onNavigate('dashboard')}
              className="hidden lg:flex items-center gap-2 bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-400 hover:to-emerald-500 text-slate-950 font-bold px-3.5 py-1.5 rounded-xl text-xs shadow-[0_0_15px_rgba(16,185,129,0.3)] transition-all cursor-pointer"
            >
              <span>Launch App</span>
            </button>

            {/* Mobile hamburger menu */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-xl bg-slate-900 text-slate-300 border border-white/10 cursor-pointer"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer Menu */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden bg-slate-950 border-b border-white/10 px-4 py-4 space-y-3"
          >
            <div className="mb-2">
              <StockSelector selectedSymbol={selectedSymbol} onSelectStock={onSelectStock} />
            </div>

            <div className="grid grid-cols-2 gap-2">
              {navItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => {
                    onNavigate(item.id);
                    setMobileMenuOpen(false);
                  }}
                  className={`flex items-center gap-2 p-2.5 rounded-xl text-xs font-semibold text-left transition-colors ${
                    activePage === item.id
                      ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                      : 'bg-slate-900 text-slate-300 border border-white/5'
                  }`}
                >
                  {item.icon}
                  <span>{item.label}</span>
                </button>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
};
