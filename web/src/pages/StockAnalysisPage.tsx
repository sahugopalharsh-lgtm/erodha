import React from 'react';
import { StockSelector } from '../components/ui/StockSelector';
import { MainPriceChart } from '../components/charts/MainPriceChart';
import { useStock, useStocks } from '../hooks/useApi';
import { formatCurrency, formatPercent } from '../utils/formatters';
import { Layers } from 'lucide-react';

interface StockAnalysisPageProps {
  selectedSymbol: string;
  onSelectStock: (symbol: string) => void;
}

export const StockAnalysisPage: React.FC<StockAnalysisPageProps> = ({
  selectedSymbol,
  onSelectStock,
}) => {
  const { stock } = useStock(selectedSymbol);
  const { stocks: allStocks } = useStocks();

  return (
    <div className="space-y-8 py-6 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-white/5 pb-6">
        <div>
          <span className="text-xs font-mono font-bold text-emerald-400 uppercase tracking-widest">
            QUANTITATIVE EQUITY DEEP-DIVE
          </span>
          <h1 className="text-3xl font-extrabold text-slate-100 tracking-tight mt-1">
            {stock.symbol} — Asset Analysis
          </h1>
          <p className="text-xs text-slate-400 mt-0.5 max-w-xl">
            {stock.name} • {stock.sector}
          </p>
        </div>

        <StockSelector selectedSymbol={selectedSymbol} onSelectStock={onSelectStock} />
      </div>

      {/* Overview Card */}
      <div className="glass-panel rounded-2xl p-6 border border-white/5 grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="md:col-span-2 space-y-2">
          <h3 className="text-sm font-bold text-slate-200">Asset Profile</h3>
          <p className="text-xs text-slate-400 leading-relaxed">{stock.description}</p>
          <div className="pt-2 flex flex-wrap gap-2 text-[11px] font-mono text-slate-300">
            <span className="bg-slate-900 px-2.5 py-1 rounded border border-white/5">Market Cap: {stock.marketCap}</span>
            <span className="bg-slate-900 px-2.5 py-1 rounded border border-white/5">24h Vol: {stock.volume}</span>
            <span className="bg-slate-900 px-2.5 py-1 rounded border border-white/5">Beta: {stock.beta}</span>
          </div>
        </div>

        <div className="bg-slate-950/60 p-4 rounded-xl border border-white/5 space-y-2 font-mono text-xs">
          <span className="text-[10px] text-slate-400 uppercase tracking-wider font-sans block font-semibold">Continuous Drift & Vol</span>
          <div className="flex justify-between text-slate-300">
            <span>Annual Drift μ:</span>
            <span className="text-emerald-400 font-bold">14.0%</span>
          </div>
          <div className="flex justify-between text-slate-300">
            <span>Volatility σ:</span>
            <span className="text-slate-100 font-bold">{stock.volatility}%</span>
          </div>
          <div className="flex justify-between text-slate-300">
            <span>Sharpe Ratio:</span>
            <span className="text-emerald-400 font-bold">{stock.sharpeRatio}</span>
          </div>
        </div>

        <div className="bg-rose-500/10 p-4 rounded-xl border border-rose-500/20 space-y-2 font-mono text-xs">
          <span className="text-[10px] text-rose-400 uppercase tracking-wider font-sans block font-semibold">Merton Jump Parameters</span>
          <div className="flex justify-between text-slate-300">
            <span>Jump Frequency λ:</span>
            <span className="text-rose-400 font-bold">{stock.jumpFrequency} / yr</span>
          </div>
          <div className="flex justify-between text-slate-300">
            <span>Mean Jump Size J:</span>
            <span className="text-rose-400 font-bold">{stock.meanJumpSize}%</span>
          </div>
          <div className="flex justify-between text-slate-300">
            <span>VaR 95%:</span>
            <span className="text-rose-400 font-bold">₹{stock.var95}</span>
          </div>
        </div>
      </div>

      {/* Main Stock Chart */}
      <MainPriceChart symbol={selectedSymbol} />

      {/* Asset Peer Comparison Table */}
      <div className="glass-panel rounded-2xl p-6 border border-white/5">
        <h3 className="text-base font-bold text-slate-100 mb-4 flex items-center gap-2">
          <Layers className="w-4 h-4 text-emerald-400" />
          <span>Equities Jump-Diffusion Matrix</span>
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs">
            <thead>
              <tr className="border-b border-white/10 text-slate-400 uppercase text-[10px] tracking-wider">
                <th className="pb-3 font-sans">Ticker</th>
                <th className="pb-3 font-sans">Price</th>
                <th className="pb-3 font-sans">24h Change</th>
                <th className="pb-3 font-sans">Vol (σ)</th>
                <th className="pb-3 font-sans">30D Forecast</th>
                <th className="pb-3 font-sans">VaR 95%</th>
                <th className="pb-3 font-sans">Jump λ</th>
                <th className="pb-3 font-sans">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5 text-slate-200">
              {allStocks.map((s) => (
                <tr key={s.symbol} className={s.symbol === selectedSymbol ? 'bg-emerald-500/10 font-bold' : 'hover:bg-slate-800/40'}>
                  <td className="py-3 font-sans font-bold text-slate-100">{s.symbol}</td>
                  <td className="py-3">{formatCurrency(s.currentPrice)}</td>
                  <td className={`py-3 ${s.dailyChange >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {formatPercent(s.dailyChange)}
                  </td>
                  <td className="py-3">{s.volatility}%</td>
                  <td className="py-3 text-blue-400">{formatCurrency(s.forecastPrice)}</td>
                  <td className="py-3 text-rose-400">₹{s.var95}</td>
                  <td className="py-3">{s.jumpFrequency} / yr</td>
                  <td className="py-3">
                    <button
                      onClick={() => onSelectStock(s.symbol)}
                      className="text-[11px] text-emerald-400 hover:text-emerald-300 font-sans cursor-pointer underline"
                    >
                      Select
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
