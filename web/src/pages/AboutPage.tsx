import React from 'react';
import { PageId } from '../types';
import { motion } from 'framer-motion';
import {
  Database,
  Sliders,
  Calculator,
  Cpu,
  Zap,
  TrendingUp,
  ShieldCheck,
  Code2,
  GraduationCap,
  ArrowRight,
  Terminal,
} from 'lucide-react';

interface AboutPageProps {
  onNavigate: (page: PageId) => void;
}

export const AboutPage: React.FC<AboutPageProps> = ({ onNavigate }) => {
  const pipelineSteps = [
    { name: 'Historical Data', desc: 'NSE tick & closing prices', icon: <Database className="w-4 h-4 text-emerald-400" /> },
    { name: 'Data Preprocessing', desc: 'Log return calculation & cleaning', icon: <Sliders className="w-4 h-4 text-blue-400" /> },
    { name: 'Return Calculation', desc: 'Continuous & discrete return series', icon: <Calculator className="w-4 h-4 text-purple-400" /> },
    { name: 'Parameter Estimation', desc: 'MLE for μ, σ, λ, μ_J, σ_J', icon: <Cpu className="w-4 h-4 text-amber-400" /> },
    { name: 'Jump-Diffusion Model', desc: 'Merton stochastic process setup', icon: <Zap className="w-4 h-4 text-rose-400" /> },
    { name: 'Monte Carlo Simulation', desc: '5,000 stochastic trajectory paths', icon: <Terminal className="w-4 h-4 text-teal-400" /> },
    { name: 'Forecast', desc: '90% confidence cone projections', icon: <TrendingUp className="w-4 h-4 text-emerald-400" /> },
    { name: 'Risk Assessment', desc: 'Empirical VaR 95/99 & Max Drawdown', icon: <ShieldCheck className="w-4 h-4 text-rose-400" /> },
  ];

  const techStack = [
    { category: 'Quantitative Computing', name: 'Python 3.12', desc: 'Core mathematical engine & stochastic SDE simulation algorithms.' },
    { category: 'Linear Algebra & Vectors', name: 'NumPy', desc: 'High-performance vector operations and Box-Muller random number generation.' },
    { category: 'Data Wrangling', name: 'Pandas', desc: 'Time-series manipulation, rolling window statistics, and log-return transformations.' },
    { category: 'Statistical Inference', name: 'SciPy', desc: 'Maximum Likelihood Estimation (MLE) for Poisson-Gaussian jump parameter fitting.' },
    { category: 'Visualizations', name: 'Recharts & Plotly', desc: 'Interactive financial chart components and stochastic path rendering.' },
    { category: 'Frontend Architecture', name: 'React 19 & TypeScript', desc: 'Modern reactive fintech UI with strict type-safety and modular architecture.' },
    { category: 'Motion Design', name: 'Framer Motion', desc: 'High-performance hardware-accelerated animations and page transitions.' },
    { category: 'Styling & Polish', name: 'Tailwind CSS v4', desc: 'Dark-first glassmorphism design system with custom utility styling.' },
  ];

  return (
    <div className="space-y-12 py-6 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="border-b border-white/5 pb-6">
        <div className="flex items-center gap-2 text-xs font-mono font-bold text-emerald-400 uppercase tracking-widest">
          <GraduationCap className="w-4 h-4" /> B.TECH MATHEMATICS & COMPUTING CAPSTONE
        </div>
        <h1 className="text-3xl sm:text-5xl font-extrabold text-slate-100 tracking-tight mt-2">
          Inside ERODHA
        </h1>
        <p className="text-sm sm:text-base text-slate-300 mt-2 max-w-3xl leading-relaxed">
          ERODHA is a quantitative stock forecasting and risk assessment system developed as a mathematical computing project. It bridges theoretical stochastic calculus with modern fintech product design.
        </p>
      </div>

      {/* Project Overview Card */}
      <div className="glass-panel rounded-2xl p-6 lg:p-8 border border-white/10 space-y-4">
        <h2 className="text-xl font-bold text-slate-100">Project Mission & Mathematical Foundation</h2>
        <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
          Standard financial models like traditional Black-Scholes rely on Geometric Brownian Motion, which assumes asset price returns are normally distributed. In real equity markets—especially Indian blue-chip stocks like RELIANCE, TCS, and INFY—prices experience sudden discontinuous shocks caused by earnings releases, macroeconomic policy shifts, and geopolitical events.
        </p>
        <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
          ERODHA addresses this gap by implementing Merton's Jump-Diffusion model. By combining continuous Gaussian random walks with discrete Poisson jump processes, ERODHA models leptokurtic fat-tail risks and generates realistic Monte Carlo future scenarios.
        </p>
      </div>

      {/* Methodology Pipeline Flowchart */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-slate-100">End-to-End Quantitative Pipeline</h2>
          <span className="text-xs font-mono text-emerald-400 font-semibold">8-Stage Architecture</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {pipelineSteps.map((step, idx) => (
            <motion.div
              key={step.name}
              initial={{ opacity: 0, y: 15 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.3, delay: idx * 0.05 }}
              className="glass-panel p-4 rounded-xl border border-white/5 relative group hover:border-emerald-500/30 transition-colors"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] font-mono text-slate-500 font-bold">STAGE 0{idx + 1}</span>
                <div className="p-1.5 rounded-lg bg-slate-900 border border-white/10">{step.icon}</div>
              </div>
              <h3 className="text-xs font-bold text-slate-100 mb-0.5">{step.name}</h3>
              <p className="text-[11px] text-slate-400 font-mono">{step.desc}</p>

              {idx < pipelineSteps.length - 1 && (
                <div className="hidden lg:block absolute -right-2 top-1/2 -translate-y-1/2 z-20 text-slate-600">
                  <ArrowRight className="w-3.5 h-3.5" />
                </div>
              )}
            </motion.div>
          ))}
        </div>
      </div>

      {/* Tech Stack Grid */}
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <Code2 className="w-5 h-5 text-emerald-400" />
          <h2 className="text-xl font-bold text-slate-100">Technology & Framework Stack</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {techStack.map((tech) => (
            <div key={tech.name} className="glass-panel p-4 rounded-xl border border-white/5 space-y-1">
              <span className="text-[9px] font-mono text-emerald-400 uppercase tracking-widest font-semibold block">
                {tech.category}
              </span>
              <h3 className="text-sm font-bold text-slate-100">{tech.name}</h3>
              <p className="text-xs text-slate-400 leading-relaxed">{tech.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* CTA to Dashboard */}
      <div className="pt-6 border-t border-white/5 text-center">
        <button
          onClick={() => onNavigate('dashboard')}
          className="inline-flex items-center gap-2 bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-400 hover:to-emerald-500 text-slate-950 font-bold px-6 py-3 rounded-xl text-xs shadow-[0_0_25px_rgba(16,185,129,0.3)] transition-all cursor-pointer"
        >
          <span>Return to Dashboard</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
