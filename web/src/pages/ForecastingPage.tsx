import React, { useState } from 'react';
import { StockSelector } from '../components/ui/StockSelector';
import { MainPriceChart } from '../components/charts/MainPriceChart';
import { MonteCarloChart } from '../components/charts/MonteCarloChart';
import { useStock, useForecast } from '../hooks/useApi';
import { formatCurrency } from '../utils/formatters';
import { AlertCircle, Sparkles } from 'lucide-react';

interface ForecastingPageProps {
  selectedSymbol: string;
  onSelectStock: (symbol: string) => void;
}

export const ForecastingPage: React.FC<ForecastingPageProps> = ({
  selectedSymbol,
  onSelectStock,
}) => {
  const [horizon, setHorizon] = useState<number>(30); // 7, 30, 90 days
  const { stock } = useStock(selectedSymbol);
  const { forecast } = useForecast(selectedSymbol, horizon);

  const forecastPrice = forecast?.medianTargetPrice ?? stock.forecastPrice;
  const expectedReturn = forecast?.expectedReturnPct ?? stock.forecastChange;
  const upperBand = forecast?.upperBound ?? Number((forecastPrice * 1.065).toFixed(2));
  const lowerBand = forecast?.lowerBound ?? Number((forecastPrice * 0.935).toFixed(2));

  return (
    <div className="space-y-8 py-6 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-white/5 pb-6">
        <div>
          <span className="text-xs font-mono font-bold text-blue-400 uppercase tracking-widest flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5" /> STOCHASTIC PROJECTION ENGINE
          </span>
          <h1 className="text-3xl font-extrabold text-slate-100 tracking-tight mt-1">
            Forecast the possible.
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Merton Jump-Diffusion stochastic price trajectories for {stock.symbol}
          </p>
        </div>

        <StockSelector selectedSymbol={selectedSymbol} onSelectStock={onSelectStock} />
      </div>

      {/* Prominent Disclaimer Callout */}
      <div className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-xl flex items-start gap-3 text-xs text-blue-200">
        <AlertCircle className="w-5 h-5 text-blue-400 shrink-0 mt-0.5" />
        <div>
          <span className="font-bold block text-blue-100">Model-Estimated Future Scenarios Disclaimer</span>
          "Forecasts are model-generated scenarios and should not be interpreted as guaranteed future prices or financial advice. ERODHA models stochastic probability densities, not deterministic outcomes."
        </div>
      </div>

      {/* Primary Forecast Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-panel p-5 rounded-xl border border-white/5">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block">Current Spot Price</span>
          <div className="text-2xl font-mono-num font-bold text-slate-100 mt-1">{formatCurrency(stock.currentPrice)}</div>
          <div className="text-[11px] text-slate-400 mt-1 font-mono">NSE Live Feed</div>
        </div>

        <div className="glass-panel p-5 rounded-xl border border-blue-500/20 bg-blue-500/5">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-blue-400 block">Median Forecast ({horizon}D)</span>
          <div className="text-2xl font-mono-num font-bold text-blue-400 mt-1">{formatCurrency(forecastPrice)}</div>
          <div className="text-[11px] text-emerald-400 mt-1 font-mono font-semibold">
            Expected Return: +{expectedReturn}%
          </div>
        </div>

        <div className="glass-panel p-5 rounded-xl border border-white/5">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block">90% Confidence Interval</span>
          <div className="text-sm font-mono-num font-bold text-slate-200 mt-2">
            {formatCurrency(lowerBand)} — {formatCurrency(upperBand)}
          </div>
          <div className="text-[11px] text-slate-400 mt-1 font-mono">Stochastic Range</div>
        </div>

        <div className="glass-panel p-5 rounded-xl border border-white/5">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block">Simulated Scenarios</span>
          <div className="text-2xl font-mono-num font-bold text-emerald-400 mt-1">5,000 Paths</div>
          <div className="text-[11px] text-slate-400 mt-1 font-mono">Poisson Jump λ={stock.jumpFrequency}</div>
        </div>
      </div>

      {/* Main Historical -> Forecast Transition Visualizer */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-slate-100">Historical → Forecast Transition Cone</h2>
          <div className="flex items-center gap-2 bg-slate-900/90 p-1 rounded-xl border border-white/10 text-xs font-mono">
            <span className="text-[10px] text-slate-400 px-2 uppercase font-semibold">Horizon:</span>
            {[7, 30, 90].map((d) => (
              <button
                key={d}
                onClick={() => setHorizon(d)}
                className={`px-2.5 py-1 rounded-lg cursor-pointer ${horizon === d ? 'bg-blue-500 text-slate-950 font-bold' : 'text-slate-400'}`}
              >
                {d}D
              </button>
            ))}
          </div>
        </div>

        <MainPriceChart symbol={selectedSymbol} />
      </div>

      {/* Simulated Scenarios Path Visualizer */}
      <MonteCarloChart stock={stock} />
    </div>
  );
};
