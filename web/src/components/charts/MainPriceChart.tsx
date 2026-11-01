import React, { useState, useMemo } from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';
import type { TimeSeriesDataPoint } from '../../types';
import { formatCurrency, formatPercent } from '../../utils/formatters';
import { useStockHistory } from '../../hooks/useApi';
import { motion } from 'framer-motion';

interface MainPriceChartProps {
  symbol: string;
  onTimeframeChange?: (tf: string) => void;
}

const TIMEFRAMES = ['1D', '1W', '1M', '3M', '6M', '1Y', '5Y'];

export const MainPriceChart: React.FC<MainPriceChartProps> = ({ symbol }) => {
  const [timeframe, setTimeframe] = useState<string>('6M');
  const [showMA, setShowMA] = useState<boolean>(true);
  const [showForecast, setShowForecast] = useState<boolean>(true);

  // Fetch real chart data from backend
  const { data: apiData } = useStockHistory(symbol, timeframe);

  // Combine historical and forecast for seamless rendering
  const combinedData = useMemo(() => {
    const rawData: { historical: TimeSeriesDataPoint[]; forecast: TimeSeriesDataPoint[] } =
      apiData || { historical: [], forecast: [] };
    const historical = rawData.historical || [];
    const forecast = rawData.forecast || [];

    const historicalMapped = historical.map((pt, idx, arr) => {
      const prevPrice = idx > 0 ? arr[idx - 1].price : pt.price;
      const dailyRet = ((pt.price - prevPrice) / prevPrice) * 100;
      return {
        ...pt,
        dailyReturn: dailyRet,
        type: 'historical',
      };
    });

    if (!showForecast) return historicalMapped;

    // Attach forecast points
    const forecastMapped = forecast.map((pt) => ({
      ...pt,
      dailyReturn: 0.15,
      type: 'forecast',
    }));

    return [...historicalMapped, ...forecastMapped];
  }, [apiData, symbol, timeframe, showForecast]);

  const raw: { historical: TimeSeriesDataPoint[] } = apiData || { historical: [] };
  const historicalSeries = raw.historical || [];
  const lastPrice = historicalSeries[historicalSeries.length - 1]?.price || 0;
  const startPrice = historicalSeries[0]?.price || lastPrice;
  const totalReturnPct = (apiData?.totalReturnPct) ?? (((lastPrice - startPrice) / Math.max(1, startPrice)) * 100);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="glass-panel rounded-2xl p-6 border border-white/5 relative overflow-hidden shadow-xl"
    >
      {/* Header controls & timeframes */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        <div>
          <div className="flex items-center gap-3">
            <h2 className="text-xl font-bold text-slate-100">{symbol} Price & Forecast Trajectory</h2>
            <span className={`text-xs font-mono font-bold px-2.5 py-1 rounded-full ${totalReturnPct >= 0 ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'}`}>
              {formatPercent(totalReturnPct)} ({timeframe})
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Historical price path, 20-Day Moving Average & Merton Jump-Diffusion projected confidence cone.
          </p>
        </div>

        {/* Controls */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Toggles */}
          <div className="flex items-center gap-2 bg-slate-900/80 p-1 rounded-xl border border-white/10 text-xs">
            <button
              onClick={() => setShowMA(!showMA)}
              className={`px-2.5 py-1 rounded-lg transition-colors cursor-pointer font-medium ${showMA ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' : 'text-slate-400 hover:text-slate-200'}`}
            >
              MA (20)
            </button>
            <button
              onClick={() => setShowForecast(!showForecast)}
              className={`px-2.5 py-1 rounded-lg transition-colors cursor-pointer font-medium ${showForecast ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30' : 'text-slate-400 hover:text-slate-200'}`}
            >
              Forecast Cone
            </button>
          </div>

          {/* Timeframe selector */}
          <div className="flex items-center bg-slate-900/80 p-1 rounded-xl border border-white/10 text-xs">
            {TIMEFRAMES.map((tf) => (
              <button
                key={tf}
                onClick={() => setTimeframe(tf)}
                className={`px-3 py-1 rounded-lg font-mono font-semibold transition-all cursor-pointer ${
                  timeframe === tf
                    ? 'bg-emerald-500 text-slate-950 shadow-md font-bold'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
                }`}
              >
                {tf}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Chart container */}
      <div className="h-[380px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={combinedData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
            <defs>
              <linearGradient id="mainForecastGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.2} />
                <stop offset="100%" stopColor="#3b82f6" stopOpacity={0.01} />
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
            <XAxis
              dataKey="date"
              stroke="#64748b"
              fontSize={11}
              tickLine={false}
              axisLine={false}
              minTickGap={25}
            />
            <YAxis
              domain={['auto', 'auto']}
              stroke="#64748b"
              fontSize={11}
              tickLine={false}
              axisLine={false}
              tickFormatter={(v) => `₹${v.toLocaleString('en-IN')}`}
            />
            <Tooltip
              content={({ active, payload }) => {
                if (!active || !payload || !payload.length) return null;
                const p = payload[0].payload;
                return (
                  <div className="bg-slate-900/95 border border-white/15 p-3 rounded-xl shadow-2xl backdrop-blur-md text-xs font-mono space-y-1">
                    <div className="text-slate-400 font-bold border-b border-white/10 pb-1 flex justify-between gap-4">
                      <span>{p.date}</span>
                      <span className="uppercase text-[10px] text-emerald-400 font-sans">{p.type}</span>
                    </div>

                    {p.price !== undefined && (
                      <div className="flex justify-between gap-6 text-slate-100">
                        <span className="text-slate-400">Price:</span>
                        <span className="font-bold">{formatCurrency(p.price)}</span>
                      </div>
                    )}

                    {p.ma20 && showMA && (
                      <div className="flex justify-between gap-6 text-amber-400">
                        <span className="text-slate-400">MA 20:</span>
                        <span>{formatCurrency(p.ma20)}</span>
                      </div>
                    )}

                    {p.isJump && (
                      <div className="text-rose-400 font-bold text-[11px] pt-1">
                        ⚡ Jump Event Recorded
                      </div>
                    )}

                    {p.forecast && showForecast && (
                      <>
                        <div className="flex justify-between gap-6 text-blue-400 font-bold pt-1 border-t border-white/10">
                          <span>Forecast Target:</span>
                          <span>{formatCurrency(p.forecast)}</span>
                        </div>
                        <div className="text-[10px] text-slate-400">
                          Upper: {formatCurrency(p.confidenceUpper)}
                        </div>
                        <div className="text-[10px] text-slate-400">
                          Lower: {formatCurrency(p.confidenceLower)}
                        </div>
                      </>
                    )}
                  </div>
                );
              }}
            />

            <Legend
              verticalAlign="top"
              align="right"
              height={36}
              iconType="circle"
              formatter={(value) => <span className="text-xs font-medium text-slate-300 mr-4">{value}</span>}
            />

            {/* Confidence Upper Area */}
            {showForecast && (
              <Area
                type="monotone"
                dataKey="confidenceUpper"
                stroke="none"
                fill="url(#mainForecastGrad)"
                name="90% Confidence Region"
              />
            )}

            {/* Historical Price Line */}
            <Line
              type="monotone"
              dataKey="price"
              stroke="#10b981"
              strokeWidth={2}
              dot={false}
              name="Historical Price"
            />

            {/* Moving Average */}
            {showMA && (
              <Line
                type="monotone"
                dataKey="ma20"
                stroke="#f59e0b"
                strokeWidth={1.5}
                strokeDasharray="3 3"
                dot={false}
                name="20-Day SMA"
              />
            )}

            {/* Forecast Line */}
            {showForecast && (
              <Line
                type="monotone"
                dataKey="forecast"
                stroke="#3b82f6"
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={false}
                name="Jump-Diffusion Forecast"
              />
            )}
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
};
