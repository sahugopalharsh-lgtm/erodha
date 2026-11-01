import React from 'react';
import { StockSelector } from '../components/ui/StockSelector';
import { ReturnHistogramChart } from '../components/charts/ReturnHistogramChart';
import { RiskGauge } from '../components/ui/RiskGauge';
import { useStock, useRisk } from '../hooks/useApi';
import { ShieldAlert } from 'lucide-react';

interface RiskAnalysisPageProps {
  selectedSymbol: string;
  onSelectStock: (symbol: string) => void;
}

export const RiskAnalysisPage: React.FC<RiskAnalysisPageProps> = ({
  selectedSymbol,
  onSelectStock,
}) => {
  const { stock } = useStock(selectedSymbol);
  const { risk } = useRisk(selectedSymbol, 1);

  const vol = risk?.volatilityAnnualPct ?? stock.volatility;
  const var95 = risk?.var95Amount ?? stock.var95;
  const var99 = risk?.var99Amount ?? stock.var99;
  const maxDd = risk?.maxDrawdownPct ?? stock.maxDrawdown;
  const jumpFreq = risk?.jumpFrequency ?? stock.jumpFrequency;
  const meanJump = risk?.meanJumpSizePct ?? stock.meanJumpSize;
  const score = risk?.riskScore ?? Math.round(vol * 2.1);
  const level = risk?.riskLevel ?? (vol > 22 ? 'HIGH' : vol > 18 ? 'MODERATE' : 'LOW');
  const es95 = risk?.expectedShortfall95Amount ?? Number((var95 * 1.35).toFixed(2));

  return (
    <div className="space-y-8 py-6 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-white/5 pb-6">
        <div>
          <span className="text-xs font-mono font-bold text-rose-400 uppercase tracking-widest flex items-center gap-1.5">
            <ShieldAlert className="w-3.5 h-3.5" /> QUANTITATIVE RISK & TAIL ASSESSMENT
          </span>
          <h1 className="text-3xl font-extrabold text-slate-100 tracking-tight mt-1">
            Analytical Risk Dashboard
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Value at Risk (VaR), Extreme Tail Risk, and Jump Frequency metrics for {stock.symbol}
          </p>
        </div>

        <StockSelector selectedSymbol={selectedSymbol} onSelectStock={onSelectStock} />
      </div>

      {/* Risk Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="glass-panel p-5 rounded-xl border border-white/5">
          <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 block">Annual Volatility (σ)</span>
          <div className="text-2xl font-mono-num font-bold text-slate-100 mt-1">{vol}%</div>
          <span className="text-[10px] text-slate-400 font-mono">Continuous Noise</span>
        </div>

        <div className="glass-panel p-5 rounded-xl border border-rose-500/20 bg-rose-500/5">
          <span className="text-[10px] font-semibold uppercase tracking-wider text-rose-400 block">Value at Risk (95%)</span>
          <div className="text-2xl font-mono-num font-bold text-rose-400 mt-1">₹{var95}</div>
          <span className="text-[10px] text-slate-400 font-mono">1-Day Max Expected Loss</span>
        </div>

        <div className="glass-panel p-5 rounded-xl border border-rose-500/20 bg-rose-500/5">
          <span className="text-[10px] font-semibold uppercase tracking-wider text-rose-400 block">Value at Risk (99%)</span>
          <div className="text-2xl font-mono-num font-bold text-rose-400 mt-1">₹{var99}</div>
          <span className="text-[10px] text-slate-400 font-mono">Extreme Tail Bound</span>
        </div>

        <div className="glass-panel p-5 rounded-xl border border-white/5">
          <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 block">Maximum Drawdown</span>
          <div className="text-2xl font-mono-num font-bold text-rose-400 mt-1">{maxDd}%</div>
          <span className="text-[10px] text-slate-400 font-mono">Historical Shock Peak-to-Trough</span>
        </div>

        <div className="glass-panel p-5 rounded-xl border border-white/5">
          <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 block">Jump Intensity (λ)</span>
          <div className="text-2xl font-mono-num font-bold text-amber-400 mt-1">{jumpFreq} / yr</div>
          <span className="text-[10px] text-slate-400 font-mono">Mean Jump: {meanJump}%</span>
        </div>
      </div>

      {/* Main Risk Gauge */}
      <RiskGauge
        score={score}
        level={level}
        var95={`₹${Number(var95).toFixed(2)}`}
        maxDrawdown={`${Number(maxDd).toFixed(2)}%`}
      />

      {/* Return Distribution Histogram with Left Tail Highlight */}
      <ReturnHistogramChart distribution={risk?.returnDistribution} />

      {/* Advanced Stress Testing Details */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-panel rounded-xl p-5 border border-white/5 space-y-2">
          <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">Parametric vs Empirical VaR</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Standard Gaussian VaR assumes a normal distribution, severely underestimating 99% tail losses. ERODHA’s empirical Jump-Diffusion Monte Carlo incorporates Poisson shock distributions.
          </p>
        </div>

        <div className="glass-panel rounded-xl p-5 border border-white/5 space-y-2">
          <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">Expected Shortfall (CVaR)</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Expected Shortfall measures the average loss in scenarios where returns fall beyond the 95% VaR threshold. For {stock.symbol}, CVaR is estimated at ₹{es95.toFixed(2)}.
          </p>
        </div>

        <div className="glass-panel rounded-xl p-5 border border-white/5 space-y-2">
          <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">Sharpe Ratio & Risk Premium</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Sharpe ratio of {stock.sharpeRatio} indicates risk-adjusted excess returns per unit of total risk (continuous volatility + jump variance).
          </p>
        </div>
      </div>
    </div>
  );
};
