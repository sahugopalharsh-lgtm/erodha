import React from 'react';
import { PageId } from '../types';
import { MetricCard } from '../components/ui/MetricCard';
import { StockSelector } from '../components/ui/StockSelector';
import { MainPriceChart } from '../components/charts/MainPriceChart';
import { MonteCarloChart } from '../components/charts/MonteCarloChart';
import { RiskGauge } from '../components/ui/RiskGauge';
import { useStock } from '../hooks/useApi';
import { motion } from 'framer-motion';
import { ArrowUpRight, ShieldAlert, Radio } from 'lucide-react';

interface DashboardPageProps {
  selectedSymbol: string;
  onSelectStock: (symbol: string) => void;
  onNavigate: (page: PageId) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  selectedSymbol,
  onSelectStock,
  onNavigate,
}) => {
  const { stock, loading } = useStock(selectedSymbol);

  return (
    <div className="space-y-8 py-6 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      {/* Header bar with title & stock selector */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-white/5 pb-6">
        <div>
          <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${loading ? 'bg-amber-400 animate-ping' : 'bg-emerald-400 animate-pulse'}`} />
            <span className="text-xs font-mono font-bold text-emerald-400 uppercase tracking-widest flex items-center gap-1.5">
              <Radio className="w-3.5 h-3.5 text-emerald-400" />
              {loading ? 'SYNCING QUANT ENGINE...' : `FEED: ${stock.dataSource || 'NSE/BSE'}`}
            </span>
          </div>
          <h1 className="text-3xl font-extrabold text-slate-100 tracking-tight mt-1">
            Market Overview
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Quantitative view of market behavior & Jump-Diffusion stochastic projections
          </p>
        </div>

        <div className="flex items-center gap-3">
          <StockSelector selectedSymbol={selectedSymbol} onSelectStock={onSelectStock} />
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <MetricCard
          label="Current Price"
          value={stock.currentPrice}
          prefix="₹"
          change={stock.dailyChange}
          changeLabel={`Change: ₹${stock.dailyChangeAmount > 0 ? '+' : ''}${stock.dailyChangeAmount}`}
          delay={0.05}
        />

        <MetricCard
          label="Daily Change"
          value={stock.dailyChange}
          suffix="%"
          change={stock.dailyChange}
          changeLabel="24h Return"
          delay={0.1}
        />

        <MetricCard
          label="Annual Volatility"
          value={stock.volatility}
          suffix="%"
          tooltip="Annualized standard deviation (σ) of daily logarithmic returns."
          changeLabel="Continuous Noise σ"
          delay={0.15}
        />

        <MetricCard
          label="Forecast Target"
          value={stock.forecastPrice}
          prefix="₹"
          change={stock.forecastChange}
          changeLabel="30-Day Median Target"
          delay={0.2}
        />

        <MetricCard
          label="VaR (95%)"
          value={stock.var95}
          prefix="₹"
          isRiskMetric={true}
          tooltip="Maximum expected loss over 1 day with 95% confidence level."
          changeLabel="Tail Risk Bound"
          delay={0.25}
        />

        <MetricCard
          label="Max Drawdown"
          value={stock.maxDrawdown}
          suffix="%"
          isRiskMetric={true}
          tooltip="Peak-to-trough historical drop during market jump shocks."
          changeLabel="Stress Test Drop"
          delay={0.3}
        />
      </div>

      {/* Main Stock Chart */}
      <MainPriceChart symbol={selectedSymbol} />

      {/* Monte Carlo Simulation Section */}
      <MonteCarloChart stock={stock} />

      {/* Risk Assessment Panel & Quick Action Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <RiskGauge
            score={Math.round(stock.volatility * 2.1)}
            level={stock.volatility > 22 ? 'HIGH' : stock.volatility > 18 ? 'MODERATE' : 'LOW'}
            var95={`₹${stock.var95.toFixed(2)}`}
            maxDrawdown={`${stock.maxDrawdown.toFixed(2)}%`}
          />
        </div>

        {/* Quick Analytical Nav Card */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.4 }}
          className="glass-panel rounded-xl p-6 border border-white/5 flex flex-col justify-between"
        >
          <div>
            <div className="flex items-center gap-2 mb-3">
              <ShieldAlert className="w-5 h-5 text-rose-400" />
              <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
                Tail Risk & Model Details
              </h3>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed mb-4">
              Explore mathematical formulations, Poisson jump parameters (λ={stock.jumpFrequency}/yr, J={stock.meanJumpSize}%), and empirical return distributions.
            </p>

            <div className="space-y-2 font-mono text-xs text-slate-300">
              <div className="flex justify-between py-1 border-b border-white/5">
                <span className="text-slate-500">Sharpe Ratio</span>
                <span className="font-bold text-emerald-400">{stock.sharpeRatio}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-white/5">
                <span className="text-slate-500">Market Beta</span>
                <span className="font-bold text-slate-200">{stock.beta}</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-500">Jump Frequency λ</span>
                <span className="font-bold text-rose-400">{stock.jumpFrequency} / yr</span>
              </div>
            </div>
          </div>

          <div className="flex gap-2 mt-6">
            <button
              onClick={() => onNavigate('risk')}
              className="flex-1 flex items-center justify-center gap-1.5 bg-slate-900 hover:bg-slate-800 border border-white/10 text-slate-200 py-2.5 rounded-xl text-xs font-semibold cursor-pointer transition-colors"
            >
              <span>Risk Analytics</span>
              <ArrowUpRight className="w-3.5 h-3.5 text-rose-400" />
            </button>

            <button
              onClick={() => onNavigate('model')}
              className="flex-1 flex items-center justify-center gap-1.5 bg-slate-900 hover:bg-slate-800 border border-white/10 text-slate-200 py-2.5 rounded-xl text-xs font-semibold cursor-pointer transition-colors"
            >
              <span>Inspect Math</span>
              <ArrowUpRight className="w-3.5 h-3.5 text-blue-400" />
            </button>
          </div>
        </motion.div>
      </div>
    </div>
  );
};
