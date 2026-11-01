import React, { useState, useEffect, useCallback } from 'react';
import { IPOOfferingInput, IPOAnalysisResponse } from '../types';
import { api } from '../services/api';
import { formatCurrency } from '../utils/formatters';
import {
  TrendingUp,
  Award,
  AlertTriangle,
  Sparkles,
  Calculator,
  RefreshCw,
  Coins,
  ShieldAlert,
} from 'lucide-react';

export const IpoAnalysisPage: React.FC = () => {
  const [inputs, setInputs] = useState<IPOOfferingInput>({
    companyName: 'Nova FinTech Innovations Ltd.',
    sector: 'Financial Technology',
    priceBandMin: 460,
    priceBandMax: 485,
    lotSize: 30,
    issueSizeCr: 1250,
    retailQuotaPct: 35,
    peRatio: 26.4,
    sectorPe: 34.0,
    greyMarketPremium: 110,
    retailSubscriptionMultiple: 12.4,
    qibSubscriptionMultiple: 24.5,
    niiSubscriptionMultiple: 16.0,
  });

  const [analysis, setAnalysis] = useState<IPOAnalysisResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const runAnalysis = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.analyzeIPO(inputs);
      setAnalysis(res);
    } catch (err: any) {
      setError(err?.message || 'Failed to calculate IPO valuation');
    } finally {
      setLoading(false);
    }
  }, [inputs]);

  useEffect(() => {
    let active = true;
    api.analyzeIPO(inputs).then((res) => {
      if (active) setAnalysis(res);
    }).catch((err: any) => {
      if (active) setError(err?.message || 'Failed to calculate IPO valuation');
    });
    return () => {
      active = false;
    };
  }, [inputs]);

  return (
    <div className="space-y-8 py-6 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-white/5 pb-6">
        <div>
          <span className="text-xs font-mono font-bold text-teal-400 uppercase tracking-widest flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5" /> SEBI LOTTERY & VALUATION ENGINE
          </span>
          <h1 className="text-3xl font-extrabold text-slate-100 tracking-tight mt-1">
            IPO Quantitative Analyzer
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Valuation against sector benchmarks, computerized lottery allotment odds, and scenario listing gains
          </p>
        </div>

        <button
          onClick={runAnalysis}
          disabled={loading}
          className="flex items-center gap-2 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-bold px-4 py-2 rounded-xl text-xs shadow-lg transition-all cursor-pointer disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>{loading ? 'Re-Computing...' : 'Re-Evaluate Offering'}</span>
        </button>
      </div>

      {/* Main Grid: Parameters Form on Left, Analytical Results on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Form: Offering Parameters */}
        <div className="lg:col-span-5 space-y-6">
          <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-5">
            <div className="flex items-center justify-between border-b border-white/5 pb-3">
              <h2 className="text-sm font-bold text-slate-100 uppercase tracking-wider flex items-center gap-2">
                <Calculator className="w-4 h-4 text-emerald-400" />
                <span>Offering Parameters</span>
              </h2>
              <span className="text-[10px] font-mono text-slate-400">Live Input</span>
            </div>

            {/* Company & Sector */}
            <div className="space-y-3">
              <div>
                <label className="text-xs text-slate-300 font-medium block mb-1">Company / Issuer Name</label>
                <input
                  type="text"
                  value={inputs.companyName}
                  onChange={(e) => setInputs({ ...inputs, companyName: e.target.value })}
                  className="w-full bg-slate-900 border border-white/10 rounded-xl px-3 py-2 text-xs text-slate-100 focus:border-emerald-500 outline-none transition-colors"
                />
              </div>

              <div>
                <label className="text-xs text-slate-300 font-medium block mb-1">Sector Benchmark</label>
                <input
                  type="text"
                  value={inputs.sector}
                  onChange={(e) => setInputs({ ...inputs, sector: e.target.value })}
                  className="w-full bg-slate-900 border border-white/10 rounded-xl px-3 py-2 text-xs text-slate-100 focus:border-emerald-500 outline-none transition-colors"
                />
              </div>
            </div>

            {/* Price Band & Lot Size */}
            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Floor (₹)</label>
                <input
                  type="number"
                  value={inputs.priceBandMin}
                  onChange={(e) => setInputs({ ...inputs, priceBandMin: Number(e.target.value) })}
                  className="w-full bg-slate-900 border border-white/10 rounded-xl px-3 py-2 text-xs text-slate-100 focus:border-emerald-500 outline-none"
                />
              </div>

              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Cap (₹)</label>
                <input
                  type="number"
                  value={inputs.priceBandMax}
                  onChange={(e) => setInputs({ ...inputs, priceBandMax: Number(e.target.value) })}
                  className="w-full bg-slate-900 border border-white/10 rounded-xl px-3 py-2 text-xs text-slate-100 focus:border-emerald-500 outline-none"
                />
              </div>

              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Lot Size</label>
                <input
                  type="number"
                  value={inputs.lotSize}
                  onChange={(e) => setInputs({ ...inputs, lotSize: Number(e.target.value) })}
                  className="w-full bg-slate-900 border border-white/10 rounded-xl px-3 py-2 text-xs text-slate-100 focus:border-emerald-500 outline-none"
                />
              </div>
            </div>

            {/* Grey Market Premium & Retail Subscription */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-[11px] text-emerald-400 font-semibold block mb-1">GMP in INR (₹)</label>
                <input
                  type="number"
                  value={inputs.greyMarketPremium || 0}
                  onChange={(e) => setInputs({ ...inputs, greyMarketPremium: Number(e.target.value) })}
                  className="w-full bg-slate-900 border border-emerald-500/30 rounded-xl px-3 py-2 text-xs text-emerald-400 font-mono font-bold focus:border-emerald-500 outline-none"
                />
              </div>

              <div>
                <label className="text-[11px] text-blue-400 font-semibold block mb-1">Retail Sub. (x)</label>
                <input
                  type="number"
                  step="0.5"
                  value={inputs.retailSubscriptionMultiple}
                  onChange={(e) => setInputs({ ...inputs, retailSubscriptionMultiple: Number(e.target.value) })}
                  className="w-full bg-slate-900 border border-blue-500/30 rounded-xl px-3 py-2 text-xs text-blue-400 font-mono font-bold focus:border-blue-500 outline-none"
                />
              </div>
            </div>

            {/* Valuation P/E Multiples */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Offering P/E Multiple</label>
                <input
                  type="number"
                  step="0.1"
                  value={inputs.peRatio || 0}
                  onChange={(e) => setInputs({ ...inputs, peRatio: Number(e.target.value) })}
                  className="w-full bg-slate-900 border border-white/10 rounded-xl px-3 py-2 text-xs text-slate-100 focus:border-emerald-500 outline-none"
                />
              </div>

              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Sector Benchmark P/E</label>
                <input
                  type="number"
                  step="0.1"
                  value={inputs.sectorPe || 0}
                  onChange={(e) => setInputs({ ...inputs, sectorPe: Number(e.target.value) })}
                  className="w-full bg-slate-900 border border-white/10 rounded-xl px-3 py-2 text-xs text-slate-100 focus:border-emerald-500 outline-none"
                />
              </div>
            </div>

            <button
              onClick={runAnalysis}
              className="w-full bg-slate-800 hover:bg-slate-700 border border-white/10 text-emerald-400 font-bold py-2.5 rounded-xl text-xs transition-colors cursor-pointer"
            >
              Update Valuation Models
            </button>
          </div>
        </div>

        {/* Right Panel: Valuation & Scenario Results */}
        <div className="lg:col-span-7 space-y-6">
          {error && (
            <div className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl text-xs text-rose-300">
              {error}
            </div>
          )}

          {analysis && (
            <div className="space-y-6">
              {/* Summary Cards */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="glass-panel p-4 rounded-xl border border-white/5">
                  <span className="text-[10px] uppercase text-slate-400 font-semibold block">Cut-Off Cap Price</span>
                  <div className="text-xl font-bold font-mono text-slate-100 mt-1">₹{analysis.cutOffPrice}</div>
                  <span className="text-[10px] text-slate-400">Floor: ₹{inputs.priceBandMin}</span>
                </div>

                <div className="glass-panel p-4 rounded-xl border border-white/5">
                  <span className="text-[10px] uppercase text-slate-400 font-semibold block">Min Lot Investment</span>
                  <div className="text-xl font-bold font-mono text-slate-100 mt-1">
                    {formatCurrency(analysis.minimumInvestmentPerLot)}
                  </div>
                  <span className="text-[10px] text-slate-400">{inputs.lotSize} shares / lot</span>
                </div>

                <div className="glass-panel p-4 rounded-xl border border-emerald-500/20 bg-emerald-500/5">
                  <span className="text-[10px] uppercase text-emerald-400 font-semibold block">Expected Gain</span>
                  <div className="text-xl font-bold font-mono text-emerald-400 mt-1">
                    +{analysis.expectedListingGainPct}%
                  </div>
                  <span className="text-[10px] text-emerald-400/80">Probability Weighted</span>
                </div>

                <div className="glass-panel p-4 rounded-xl border border-blue-500/20 bg-blue-500/5">
                  <span className="text-[10px] uppercase text-blue-400 font-semibold block">Retail Lottery Odds</span>
                  <div className="text-xl font-bold font-mono text-blue-400 mt-1">
                    {analysis.allotmentOdds.retailLotteryProbabilityPct}%
                  </div>
                  <span className="text-[10px] text-blue-300 font-mono">{analysis.allotmentOdds.oddsRatio}</span>
                </div>
              </div>

              {/* SEBI Lottery Allotment Mechanics Callout */}
              <div className="glass-panel p-5 rounded-2xl border border-blue-500/20 bg-blue-500/5 space-y-2">
                <div className="flex items-center gap-2">
                  <Award className="w-4 h-4 text-blue-400" />
                  <h3 className="text-xs font-bold uppercase tracking-wider text-blue-300">
                    SEBI Retail Computerized Lottery Model
                  </h3>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {analysis.allotmentOdds.description}
                </p>
                <div className="pt-2 text-[11px] font-mono text-slate-400 flex flex-wrap gap-4 border-t border-white/5">
                  <span>Retail Subscription: <strong className="text-slate-200">{analysis.allotmentOdds.retailSubscriptionMultiple}x</strong></span>
                  <span>QIB Subscription: <strong className="text-slate-200">{analysis.allotmentOdds.qibSubscriptionMultiple}x</strong></span>
                  <span>NII Subscription: <strong className="text-slate-200">{analysis.allotmentOdds.niiSubscriptionMultiple}x</strong></span>
                </div>
              </div>

              {/* Listing Scenarios (Bear, Base, Bull) */}
              <div className="glass-panel p-6 rounded-2xl border border-white/5 space-y-4">
                <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-emerald-400" />
                  <span>Day-1 Listing Scenarios Distribution</span>
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {analysis.scenarios.map((sc, idx) => {
                    const isBull = sc.name.includes('Bull');
                    const isBear = sc.name.includes('Bear');
                    const borderColor = isBull
                      ? 'border-emerald-500/30 bg-emerald-500/5'
                      : isBear
                      ? 'border-rose-500/30 bg-rose-500/5'
                      : 'border-blue-500/30 bg-blue-500/5';
                    const textColor = isBull
                      ? 'text-emerald-400'
                      : isBear
                      ? 'text-rose-400'
                      : 'text-blue-400';

                    return (
                      <div key={idx} className={`p-4 rounded-xl border ${borderColor} space-y-2`}>
                        <div className="flex justify-between items-center">
                          <span className="text-xs font-bold text-slate-200">{sc.name}</span>
                          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 border border-white/10 text-slate-400">
                            {Math.round(sc.probabilityWeight * 100)}% prob
                          </span>
                        </div>

                        <div className={`text-2xl font-mono font-bold ${textColor}`}>
                          ₹{sc.projectedListingPrice}
                        </div>

                        <div className="text-xs font-semibold font-mono">
                          Gain: <span className={sc.projectedGainPct >= 0 ? 'text-emerald-400' : 'text-rose-400'}>
                            {sc.projectedGainPct > 0 ? '+' : ''}{sc.projectedGainPct}%
                          </span>
                        </div>

                        <p className="text-[11px] text-slate-400 leading-snug pt-1">
                          {sc.description}
                        </p>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Day-1 Volatility & Value at Risk */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="glass-panel p-4 rounded-xl border border-white/5 space-y-1">
                  <div className="flex items-center gap-2 text-rose-400">
                    <ShieldAlert className="w-4 h-4" />
                    <span className="text-xs font-bold uppercase tracking-wider">Day-1 Value at Risk (95%)</span>
                  </div>
                  <div className="text-xl font-bold font-mono text-rose-400">
                    ₹{analysis.day1VaR95Amount} ({analysis.day1VaR95Pct}%)
                  </div>
                  <p className="text-[11px] text-slate-400">
                    Statistical maximum 1-day listing downside based on empirical 12% listing return volatility.
                  </p>
                </div>

                <div className="glass-panel p-4 rounded-xl border border-white/5 space-y-1">
                  <div className="flex items-center gap-2 text-emerald-400">
                    <Coins className="w-4 h-4" />
                    <span className="text-xs font-bold uppercase tracking-wider">Relative Valuation Assessment</span>
                  </div>
                  <div className="text-sm font-bold text-slate-200">
                    {analysis.valuationAnalysis.valuationStatus || 'Benchmark aligned'}
                  </div>
                  <p className="text-[11px] text-slate-400">
                    Offering P/E: {inputs.peRatio}x vs Sector benchmark: {inputs.sectorPe}x.
                  </p>
                </div>
              </div>

              {/* Transparent Disclaimer */}
              <div className="p-4 bg-slate-900/60 border border-white/5 rounded-xl flex items-start gap-3 text-xs text-slate-400">
                <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                <div className="leading-relaxed">
                  {analysis.disclaimer}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
