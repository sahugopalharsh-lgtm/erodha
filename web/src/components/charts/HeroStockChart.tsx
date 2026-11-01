import React, { useMemo } from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceDot,
} from 'recharts';
import { motion } from 'framer-motion';

export const HeroStockChart: React.FC = () => {
  // Generate realistic Hero dataset with Historical, Jump event, Forecast & Confidence band
  const data = useMemo(() => {
    const pts = [];
    const base = 2400;

    // 1. Historical normal (days 0-30)
    for (let i = 0; i <= 30; i++) {
      const normalPrice = base + i * 8 + Math.sin(i * 0.4) * 25;
      pts.push({
        day: `T-${30 - i}`,
        historical: Number(normalPrice.toFixed(2)),
        type: 'historical',
      });
    }

    // 2. Sudden Jump event (day 31)
    const lastPrice = pts[pts.length - 1].historical;
    const jumpPrice = lastPrice - 180; // Sudden -7.2% jump
    pts.push({
      day: 'JUMP',
      historical: Number(jumpPrice.toFixed(2)),
      isJump: true,
      type: 'jump',
    });

    // 3. Recovery + Forecast (days 32-60)
    let curForecast = jumpPrice;
    for (let i = 1; i <= 30; i++) {
      curForecast += 9 + Math.cos(i * 0.3) * 6;
      const spread = Math.sqrt(i) * 18;

      // Simulated path variants
      const path1 = curForecast + Math.sin(i * 0.5) * spread * 0.8;
      const path2 = curForecast - Math.cos(i * 0.6) * spread * 0.7;
      const path3 = curForecast + Math.cos(i * 0.4) * spread * 0.9;

      pts.push({
        day: `T+${i}`,
        forecast: Number(curForecast.toFixed(2)),
        upperBand: Number((curForecast + spread * 1.6).toFixed(2)),
        lowerBand: Number((curForecast - spread * 1.6).toFixed(2)),
        band: [
          Number((curForecast - spread * 1.6).toFixed(2)),
          Number((curForecast + spread * 1.6).toFixed(2)),
        ],
        path1: Number(path1.toFixed(2)),
        path2: Number(path2.toFixed(2)),
        path3: Number(path3.toFixed(2)),
        type: 'forecast',
      });
    }

    return pts;
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.96 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.8, delay: 0.2 }}
      className="glass-panel rounded-2xl p-6 border border-white/10 relative overflow-hidden shadow-2xl group"
    >
      {/* Subtle background glow */}
      <div className="absolute -top-24 -right-24 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-24 -left-24 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* Header bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6 relative z-10">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
            <h3 className="text-sm font-bold text-slate-100 tracking-wide">
              Jump-Diffusion Trajectory (illustration)
            </h3>
          </div>
          <p className="text-xs text-slate-400 mt-0.5 font-mono">
            Schematic of a sudden jump · not live market data
          </p>
        </div>

        <div className="flex items-center gap-3 text-xs font-mono">
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-900/60 border border-white/10">
            <span className="w-2 h-0.5 bg-emerald-400 rounded-full" />
            <span className="text-slate-300">Historical</span>
          </div>
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-rose-500/10 border border-rose-500/20 text-rose-400 font-bold">
            <span>⚡ Sudden Jump</span>
          </div>
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-900/60 border border-white/10">
            <span className="w-2 h-0.5 bg-blue-400 rounded-full" />
            <span className="text-slate-300">Monte Carlo Paths</span>
          </div>
        </div>
      </div>

      {/* Responsive Recharts */}
      <div className="h-[340px] w-full relative z-10">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="forecastBandGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.25} />
                <stop offset="100%" stopColor="#3b82f6" stopOpacity={0.02} />
              </linearGradient>
              <linearGradient id="histGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#10b981" stopOpacity={0.3} />
                <stop offset="100%" stopColor="#10b981" stopOpacity={0.0} />
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
            <XAxis
              dataKey="day"
              stroke="#64748b"
              fontSize={10}
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              domain={['auto', 'auto']}
              stroke="#64748b"
              fontSize={10}
              tickLine={false}
              axisLine={false}
              tickFormatter={(v) => `₹${v}`}
            />
            <Tooltip
              content={({ active, payload }) => {
                if (!active || !payload || !payload.length) return null;
                const p = payload[0].payload;
                return (
                  <div className="bg-slate-900/95 border border-white/15 p-3 rounded-lg shadow-2xl backdrop-blur-md font-mono text-xs">
                    <div className="text-slate-400 border-b border-white/10 pb-1 mb-1 font-semibold">
                      Timeline: {p.day}
                    </div>
                    {p.historical && (
                      <div className="text-emerald-400">
                        Historical: ₹{p.historical}
                      </div>
                    )}
                    {p.isJump && (
                      <div className="text-rose-400 font-bold">
                        ⚡ Jump Event (-7.2% Shock)
                      </div>
                    )}
                    {p.forecast && (
                      <>
                        <div className="text-blue-400">Median Forecast: ₹{p.forecast}</div>
                        <div className="text-slate-400 text-[10px]">
                          90% Band: ₹{p.lowerBand} – ₹{p.upperBand}
                        </div>
                      </>
                    )}
                  </div>
                );
              }}
            />

            {/* Confidence Band Area */}
            <Area
              type="monotone"
              dataKey="upperBand"
              stroke="none"
              fill="url(#forecastBandGrad)"
            />

            {/* Historical Line */}
            <Line
              type="monotone"
              dataKey="historical"
              stroke="#10b981"
              strokeWidth={2.5}
              dot={false}
              isAnimationActive={true}
              animationDuration={1500}
            />

            {/* Jump marker dot */}
            <ReferenceDot
              x="JUMP"
              y={2470}
              r={6}
              fill="#ef4444"
              stroke="#ffffff"
              strokeWidth={2}
            />

            {/* Forecast Line */}
            <Line
              type="monotone"
              dataKey="forecast"
              stroke="#3b82f6"
              strokeWidth={2.5}
              strokeDasharray="4 4"
              dot={false}
            />

            {/* Simulated paths */}
            <Line type="monotone" dataKey="path1" stroke="rgba(139, 92, 246, 0.4)" strokeWidth={1} dot={false} />
            <Line type="monotone" dataKey="path2" stroke="rgba(59, 130, 246, 0.3)" strokeWidth={1} dot={false} />
            <Line type="monotone" dataKey="path3" stroke="rgba(16, 185, 129, 0.3)" strokeWidth={1} dot={false} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Footer label */}
      <div className="mt-4 pt-3 border-t border-white/5 flex items-center justify-between text-[11px] text-slate-400">
        <span className="flex items-center gap-1.5 font-medium">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
          Powered by Jump-Diffusion Modelling & Merton Jump Process
        </span>
        <span className="font-mono text-slate-500">Confidence Band: 90% Confidence Interval</span>
      </div>
    </motion.div>
  );
};
