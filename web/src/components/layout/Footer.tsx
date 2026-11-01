import React from 'react';
import { PageId } from '../../types';

interface FooterProps {
  onNavigate: (page: PageId) => void;
}

export const Footer: React.FC<FooterProps> = ({ onNavigate }) => {
  return (
    <footer className="bg-[#090a0f] border-t border-white/10 mt-20 text-slate-400 text-xs py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-10">
          {/* Brand Info */}
          <div className="md:col-span-2 space-y-3">
            <div className="flex items-center gap-2.5">
              <div className="w-7 h-7 rounded-lg bg-emerald-500 flex items-center justify-center text-slate-950 font-mono font-extrabold text-sm">
                ∑
              </div>
              <span className="font-extrabold text-slate-100 text-base">ERODHA</span>
            </div>
            <p className="text-slate-400 text-xs leading-relaxed max-w-md">
              Quantitative stock forecasting and risk assessment engine utilizing Merton Jump-Diffusion stochastic processes and Monte Carlo simulations.
            </p>
            <div className="text-[11px] text-emerald-400 font-mono font-medium">
              Mathematics & Computing Micro-Project • B.Tech Capstone
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200 mb-3">Platform Navigation</h4>
            <ul className="space-y-2 text-xs">
              <li>
                <button onClick={() => onNavigate('dashboard')} className="hover:text-emerald-400 transition-colors cursor-pointer">
                  Market Overview
                </button>
              </li>
              <li>
                <button onClick={() => onNavigate('forecast')} className="hover:text-emerald-400 transition-colors cursor-pointer">
                  Jump-Diffusion Forecast
                </button>
              </li>
              <li>
                <button onClick={() => onNavigate('risk')} className="hover:text-emerald-400 transition-colors cursor-pointer">
                  Risk & Tail Value at Risk
                </button>
              </li>
              <li>
                <button onClick={() => onNavigate('model')} className="hover:text-emerald-400 transition-colors cursor-pointer">
                  Merton SDE Mathematics
                </button>
              </li>
              <li>
                <button onClick={() => onNavigate('about')} className="hover:text-emerald-400 transition-colors cursor-pointer">
                  Architecture & Technology Stack
                </button>
              </li>
            </ul>
          </div>

          {/* Model Tech Stack */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200 mb-3">Quantitative Stack</h4>
            <div className="flex flex-wrap gap-1.5 font-mono text-[10px]">
              <span className="bg-slate-900 border border-white/10 px-2 py-1 rounded text-slate-300">Python 3.12</span>
              <span className="bg-slate-900 border border-white/10 px-2 py-1 rounded text-slate-300">NumPy</span>
              <span className="bg-slate-900 border border-white/10 px-2 py-1 rounded text-slate-300">SciPy Stats</span>
              <span className="bg-slate-900 border border-white/10 px-2 py-1 rounded text-slate-300">React 19</span>
              <span className="bg-slate-900 border border-white/10 px-2 py-1 rounded text-slate-300">Framer Motion</span>
              <span className="bg-slate-900 border border-white/10 px-2 py-1 rounded text-slate-300">Recharts</span>
            </div>
          </div>
        </div>

        {/* Disclaimer Callout */}
        <div className="pt-6 border-t border-white/5 flex flex-col md:flex-row items-center justify-between gap-4 text-[11px] text-slate-500">
          <p>
            Disclaimer: ERODHA is a quantitative research project. Forecasts are stochastic model-generated scenarios and should not be interpreted as financial advice.
          </p>
          <p className="font-mono">© 2026 ERODHA Quant Systems</p>
        </div>
      </div>
    </footer>
  );
};
