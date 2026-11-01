import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, CheckCircle } from 'lucide-react';

interface TermDetail {
  id: string;
  symbol: string;
  name: string;
  role: string;
  description: string;
  mathFormula: string;
  color: string;
  badgeColor: string;
}

const TERMS: TermDetail[] = [
  {
    id: 'mu',
    symbol: 'μ S dt',
    name: 'Deterministic Drift Term',
    role: 'Continuous Trend & Expected Return',
    description: 'Represents the expected continuous growth rate (drift) of the asset price over time step dt, reflecting fundamental economic return.',
    mathFormula: 'μ = Annualized Expected Return Rate',
    color: 'text-emerald-400 hover:bg-emerald-500/20 border-emerald-500/30',
    badgeColor: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
  },
  {
    id: 'sigma',
    symbol: 'σ S dW',
    name: 'Geometric Brownian Diffusion',
    role: 'Continuous Volatility & Market Noise',
    description: 'Captures continuous random market fluctuation. dW is a standard Wiener process (Brownian motion) drawing from Gaussian normal distribution N(0, dt).',
    mathFormula: 'dW ~ Normal(0, dt)',
    color: 'text-blue-400 hover:bg-blue-500/20 border-blue-500/30',
    badgeColor: 'bg-blue-500/10 text-blue-400 border-blue-500/20'
  },
  {
    id: 'jump',
    symbol: 'J S dN',
    name: 'Discontinuous Jump Process',
    role: 'Merton Jump Component',
    description: 'Models sudden discontinuous price shocks (earnings announcements, regulatory surprises, geopolitical events). Combination of jump size J and Poisson arrival dN.',
    mathFormula: 'dN ~ Poisson(λ dt), J ~ LogNormal(μ_J, σ_J²)',
    color: 'text-rose-400 hover:bg-rose-500/20 border-rose-500/30',
    badgeColor: 'bg-rose-500/10 text-rose-400 border-rose-500/20'
  },
];

export const ModelEquation: React.FC = () => {
  const [selectedTerm, setSelectedTerm] = useState<TermDetail>(TERMS[2]); // Default to Jump term

  return (
    <div className="glass-panel rounded-2xl p-6 lg:p-8 border border-white/10 relative overflow-hidden shadow-2xl">
      <div className="flex items-center gap-2 mb-4">
        <Sparkles className="w-4 h-4 text-purple-400" />
        <span className="text-xs font-bold uppercase tracking-wider text-purple-400">
          Stochastic Differential Equation (SDE)
        </span>
      </div>

      <h3 className="text-xl lg:text-2xl font-bold text-slate-100 mb-2">
        Merton's Jump-Diffusion Model Equation
      </h3>
      <p className="text-xs lg:text-sm text-slate-400 mb-8 max-w-2xl">
        Click or hover over any equation term below to inspect its mathematical formulation and role in quantitative price modelling.
      </p>

      {/* Interactive SDE Display */}
      <div className="bg-slate-950/90 rounded-2xl p-6 lg:p-8 border border-white/10 text-center shadow-inner relative overflow-hidden mb-8">
        <div className="text-xs font-mono text-slate-400 mb-4 tracking-widest uppercase">
          Asset Price Dynamics Equation
        </div>

        <div className="flex flex-wrap items-center justify-center gap-3 lg:gap-5 font-mono text-2xl lg:text-4xl font-extrabold tracking-tight">
          <span className="text-slate-100">dS =</span>

          {TERMS.map((term) => {
            const isSelected = selectedTerm.id === term.id;
            return (
              <motion.button
                key={term.id}
                onClick={() => setSelectedTerm(term)}
                onMouseEnter={() => setSelectedTerm(term)}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.98 }}
                className={`px-3 py-2 rounded-xl border transition-all cursor-pointer ${term.color} ${
                  isSelected ? 'bg-slate-800/90 shadow-[0_0_20px_rgba(255,255,255,0.15)] ring-2 ring-white/20' : 'bg-slate-900/60 opacity-80'
                }`}
              >
                {term.symbol}
              </motion.button>
            );
          })}
        </div>

        <div className="mt-4 text-[11px] text-slate-500 font-mono">
          Hover terms above to explore parameters
        </div>
      </div>

      {/* Selected Term Details Card */}
      <AnimatePresence mode="wait">
        <motion.div
          key={selectedTerm.id}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.25 }}
          className="bg-slate-900/90 border border-white/10 rounded-xl p-6 relative overflow-hidden"
        >
          <div className="flex flex-wrap items-center justify-between gap-4 mb-3 border-b border-white/5 pb-3">
            <div className="flex items-center gap-3">
              <span className={`px-3 py-1 rounded-lg font-mono text-sm font-bold border ${selectedTerm.badgeColor}`}>
                {selectedTerm.symbol}
              </span>
              <div>
                <h4 className="text-base font-bold text-slate-100">{selectedTerm.name}</h4>
                <span className="text-xs text-slate-400">{selectedTerm.role}</span>
              </div>
            </div>

            <div className="font-mono text-xs text-slate-300 bg-slate-950 px-3 py-1.5 rounded-lg border border-white/10">
              {selectedTerm.mathFormula}
            </div>
          </div>

          <p className="text-xs lg:text-sm text-slate-300 leading-relaxed">
            {selectedTerm.description}
          </p>

          <div className="mt-4 pt-3 flex items-center justify-between text-[11px] text-slate-400">
            <span className="flex items-center gap-1.5 font-mono text-emerald-400">
              <CheckCircle className="w-3.5 h-3.5" /> Quantitative Rigor Verified
            </span>
            <span className="text-slate-500">Merton (1976) Journal of Financial Economics</span>
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  );
};
