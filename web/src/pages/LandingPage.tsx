import React from 'react';
import { PageId } from '../types';
import { Badge } from '../components/ui/Badge';
import { HeroStockChart } from '../components/charts/HeroStockChart';
import { JumpDiffusionInteractiveChart } from '../components/charts/JumpDiffusionInteractiveChart';
import { motion } from 'framer-motion';
import {
  ArrowRight,
  Database,
  Calculator,
  Zap,
  ShieldCheck,
  TrendingUp,
  LineChart,
  Activity,
  BarChart2,
  Sparkles,
  ChevronRight,
} from 'lucide-react';

interface LandingPageProps {
  onNavigate: (page: PageId) => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onNavigate }) => {
  const steps = [
    {
      num: '01',
      title: 'Collect',
      subtitle: 'Historical market data',
      desc: 'Ingests high-frequency tick and daily closing prices across blue-chip Indian equities.',
      icon: <Database className="w-5 h-5 text-emerald-400" />,
    },
    {
      num: '02',
      title: 'Model',
      subtitle: 'Estimate drift, volatility & jumps',
      desc: 'Decomposes returns into continuous Gaussian drift (μ, σ) and Merton Poisson jump parameters (λ, J).',
      icon: <Calculator className="w-5 h-5 text-blue-400" />,
    },
    {
      num: '03',
      title: 'Simulate',
      subtitle: 'Generate future price paths',
      desc: 'Executes thousands of stochastic Monte Carlo iterations to map complex future probability distributions.',
      icon: <Zap className="w-5 h-5 text-purple-400" />,
    },
    {
      num: '04',
      title: 'Assess',
      subtitle: 'Measure forecast uncertainty & risk',
      desc: 'Computes Value at Risk (VaR 95/99), Expected Shortfall, and Maximum Drawdown metrics.',
      icon: <ShieldCheck className="w-5 h-5 text-rose-400" />,
    },
  ];

  const features = [
    { title: 'Historical Analysis', desc: 'Deep time-series decomposition and moving average trends.', icon: <LineChart className="w-4 h-4 text-emerald-400" /> },
    { title: 'Jump Detection', desc: 'Identifies sudden discontinuous shock events in returns.', icon: <Zap className="w-4 h-4 text-rose-400" /> },
    { title: 'Monte Carlo Simulation', desc: 'Simulates 5,000+ stochastic paths per asset.', icon: <Activity className="w-4 h-4 text-blue-400" /> },
    { title: 'Price Forecasting', desc: '90% confidence cone projections for 7D, 30D & 90D horizons.', icon: <TrendingUp className="w-4 h-4 text-purple-400" /> },
    { title: 'Value at Risk (VaR)', desc: '95% and 99% parametric and empirical VaR evaluation.', icon: <ShieldCheck className="w-4 h-4 text-amber-400" /> },
    { title: 'Maximum Drawdown', desc: 'Worst-case peak-to-trough decline stress testing.', icon: <BarChart2 className="w-4 h-4 text-rose-400" /> },
  ];

  return (
    <div className="space-y-24 py-8">
      {/* Hero Section */}
      <section className="relative min-h-[85vh] flex flex-col justify-center items-center text-center px-4 bg-grid-pattern">
        {/* Subtle background glow elements */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-emerald-500/10 rounded-full blur-[120px] pointer-events-none" />

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="max-w-4xl mx-auto space-y-6"
        >
          {/* Badge */}
          <div className="inline-flex">
            <Badge variant="green">QUANTITATIVE FINANCE • STOCK ANALYTICS</Badge>
          </div>

          {/* Main Heading */}
          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold text-slate-100 tracking-tight leading-[1.1]">
            See the market <br className="hidden sm:inline" />
            <span className="bg-gradient-to-r from-emerald-400 via-teal-300 to-emerald-500 bg-clip-text text-transparent">
              beyond the normal.
            </span>
          </h1>

          {/* Subheading */}
          <p className="text-slate-300 text-base sm:text-lg lg:text-xl font-normal max-w-2xl mx-auto leading-relaxed">
            ERODHA combines historical market data, Jump-Diffusion Models and Monte Carlo Simulation to forecast possible stock-price movements and assess financial risk.
          </p>

          {/* CTAs */}
          <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
            <motion.button
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => onNavigate('dashboard')}
              className="flex items-center gap-2 bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-400 hover:to-emerald-500 text-slate-950 font-extrabold px-6 py-3.5 rounded-xl text-sm shadow-[0_0_35px_rgba(16,185,129,0.4)] transition-all cursor-pointer group"
            >
              <span>Explore Dashboard</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => onNavigate('model')}
              className="flex items-center gap-2 bg-slate-900/90 hover:bg-slate-800 text-slate-200 font-bold border border-white/10 hover:border-white/20 px-6 py-3.5 rounded-xl text-sm transition-all cursor-pointer"
            >
              <Sparkles className="w-4 h-4 text-emerald-400" />
              <span>Understand the Model</span>
            </motion.button>
          </div>
        </motion.div>

        {/* Hero Visual Chart */}
        <div className="w-full max-w-5xl mx-auto mt-14">
          <HeroStockChart />
        </div>
      </section>

      {/* Section 1: 4-Step Process */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-14">
          <span className="text-xs font-bold text-emerald-400 uppercase tracking-widest block mb-2">
            METHODOLOGY PIPELINE
          </span>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-100">
            From market data to intelligent insight.
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {steps.map((step, idx) => (
            <motion.div
              key={step.num}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: idx * 0.1 }}
              whileHover={{ y: -5 }}
              className="glass-panel-interactive rounded-2xl p-6 border border-white/5 relative group"
            >
              <div className="flex items-center justify-between mb-4">
                <span className="text-2xl font-mono font-black text-slate-600 group-hover:text-emerald-400 transition-colors">
                  {step.num}
                </span>
                <div className="p-2.5 rounded-xl bg-slate-900 border border-white/10 group-hover:border-emerald-500/30 transition-colors">
                  {step.icon}
                </div>
              </div>

              <h3 className="text-lg font-bold text-slate-100 mb-1">{step.title}</h3>
              <div className="text-xs font-semibold text-emerald-400 mb-2 font-mono">{step.subtitle}</div>
              <p className="text-xs text-slate-400 leading-relaxed">{step.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Section 2: Why Jump-Diffusion */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-14">
          <span className="text-xs font-bold text-rose-400 uppercase tracking-widest block mb-2">
            MODEL DIFFERENCE
          </span>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-100 mb-3">
            Why Jump-Diffusion?
          </h2>
          <p className="text-sm text-slate-400">
            Traditional Geometric Brownian Motion assumes prices move continuously without sudden shocks. ERODHA models reality.
          </p>
        </div>

        <JumpDiffusionInteractiveChart />
      </section>

      {/* Section 3: Built for quantitative thinking */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-14">
          <span className="text-xs font-bold text-blue-400 uppercase tracking-widest block mb-2">
            SYSTEM CAPABILITIES
          </span>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-100">
            Built for quantitative thinking.
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feat, idx) => (
            <motion.div
              key={feat.title}
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.3, delay: idx * 0.08 }}
              className="glass-panel p-5 rounded-xl border border-white/5 hover:border-white/15 transition-colors flex items-start gap-4"
            >
              <div className="p-2.5 rounded-lg bg-slate-900 border border-white/10 shrink-0 mt-0.5">
                {feat.icon}
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-100 mb-1">{feat.title}</h3>
                <p className="text-xs text-slate-400 leading-relaxed">{feat.desc}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Section 4: Final Call to Action */}
      <section className="max-w-5xl mx-auto px-4">
        <div className="glass-panel rounded-3xl p-8 lg:p-14 border border-emerald-500/30 text-center relative overflow-hidden bg-gradient-to-b from-emerald-500/10 via-slate-950 to-slate-950 shadow-2xl">
          <div className="absolute -top-24 left-1/2 -translate-x-1/2 w-96 h-96 bg-emerald-500/20 rounded-full blur-3xl pointer-events-none" />

          <h2 className="text-3xl sm:text-5xl font-extrabold text-slate-100 tracking-tight mb-4 relative z-10">
            Turn market uncertainty into measurable insight.
          </h2>
          <p className="text-slate-300 text-sm sm:text-base max-w-xl mx-auto mb-8 relative z-10">
            Access live stochastic forecasts, Monte Carlo path generators, and tail Value at Risk assessments for blue-chip equities.
          </p>

          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => onNavigate('dashboard')}
            className="inline-flex items-center gap-2.5 bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-400 hover:to-emerald-500 text-slate-950 font-extrabold px-8 py-4 rounded-xl text-base shadow-[0_0_40px_rgba(16,185,129,0.5)] transition-all cursor-pointer relative z-10 group"
          >
            <span>Launch ERODHA</span>
            <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </motion.button>
        </div>
      </section>
    </div>
  );
};
