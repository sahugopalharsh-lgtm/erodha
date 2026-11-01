import React, { useState, useMemo, useCallback, useEffect } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceLine,
} from 'recharts';
import { api } from '../../services/api';
import { Stock, MonteCarloResponse } from '../../types';

const EMPTY_SIM = { paths: [], summaryCurve: [], finalMedian: 0, finalUpper95: 0, finalLower5: 0 } as unknown as MonteCarloResponse;
import { Play, RefreshCw, Zap, ArrowRight } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface MonteCarloChartProps {
  stock: Stock;
}

export const MonteCarloChart: React.FC<MonteCarloChartProps> = ({ stock }) => {
  const [numSimulations, setNumSimulations] = useState<number>(1000);
  const [horizonDays, setHorizonDays] = useState<number>(30);
  const [isSimulating, setIsSimulating] = useState<boolean>(false);
  const [simulationSeed, setSimulationSeed] = useState<number>(1);

  // Real Monte Carlo from the Django backend (Merton jump-diffusion, MLE-calibrated)
  const [simResults, setSimResults] = useState<MonteCarloResponse>(EMPTY_SIM);
  const [simError, setSimError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setIsSimulating(true);
    api.runMonteCarlo({ symbol: stock.symbol, numSimulations, horizonDays, seed: simulationSeed })
      .then((r) => { if (!cancelled) { setSimResults(r); setSimError(null); } })
      .catch((e: any) => { if (!cancelled) setSimError(e?.message || 'Simulation failed'); })
      .finally(() => { if (!cancelled) setIsSimulating(false); });
    return () => { cancelled = true; };
  }, [stock.symbol, numSimulations, horizonDays, simulationSeed]);

  const handleRunSimulation = useCallback(() => {
    setSimulationSeed((prev) => prev + 1);
  }, []);

  // Format data for multi-line Recharts
  const chartData = useMemo(() => {
    const dataPoints: Record<string, any>[] = [];
    for (let day = 0; day <= horizonDays; day++) {
      const point: Record<string, any> = { day: `Day ${day}` };
      
      // Attach displayed paths
      simResults.paths.forEach((p) => {
        point[p.id] = p.data[day]?.price;
      });

      // Attach summary percentiles
      const summaryPoint = simResults.summaryCurve[day];
      if (summaryPoint) {
        point.median = summaryPoint.median;
        point.p95 = summaryPoint.p95;
        point.p5 = summaryPoint.p5;
      }

      dataPoints.push(point);
    }
    return dataPoints;
  }, [simResults, horizonDays]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.1 }}
      className="glass-panel rounded-2xl p-6 border border-white/5 relative overflow-hidden shadow-xl"
    >
      {/* Header & Controls */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        <div>
          <div className="flex items-center gap-2">
            <Zap className="w-5 h-5 text-emerald-400" />
            <h2 className="text-xl font-bold text-slate-100">Possible Future Paths</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Monte Carlo Jump-Diffusion engine simulating stochastic asset trajectories for {stock.symbol}.
          </p>
        </div>

        {/* Simulation Controls */}
        <div className="flex flex-wrap items-center gap-4">
          {/* Sim Count Selection */}
          <div className="flex items-center gap-1.5 bg-slate-900/90 p-1 rounded-xl border border-white/10 text-xs">
            <span className="text-[10px] text-slate-400 font-semibold px-2 uppercase">Paths:</span>
            {[100, 500, 1000, 5000].map((count) => (
              <button
                key={count}
                onClick={() => setNumSimulations(count)}
                className={`px-2.5 py-1 rounded-lg font-mono font-semibold transition-all cursor-pointer ${
                  numSimulations === count
                    ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {count}
              </button>
            ))}
          </div>

          {/* Horizon Selection */}
          <div className="flex items-center gap-1.5 bg-slate-900/90 p-1 rounded-xl border border-white/10 text-xs">
            <span className="text-[10px] text-slate-400 font-semibold px-2 uppercase">Horizon:</span>
            {[7, 30, 90].map((days) => (
              <button
                key={days}
                onClick={() => setHorizonDays(days)}
                className={`px-2.5 py-1 rounded-lg font-mono font-semibold transition-all cursor-pointer ${
                  horizonDays === days
                    ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {days}D
              </button>
            ))}
          </div>

          {/* Run Simulation Action Button */}
          <motion.button
            onClick={handleRunSimulation}
            disabled={isSimulating}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="flex items-center gap-2 bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-400 hover:to-emerald-500 text-slate-950 font-bold px-4 py-2 rounded-xl text-xs shadow-[0_0_20px_rgba(16,185,129,0.3)] transition-all cursor-pointer group"
          >
            {isSimulating ? (
              <RefreshCw className="w-4 h-4 animate-spin text-slate-950" />
            ) : (
              <Play className="w-4 h-4 fill-current text-slate-950" />
            )}
            <span>{isSimulating ? 'Simulating...' : 'Run Simulation'}</span>
            <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
          </motion.button>
        </div>
      </div>

      {simError && (
        <div className="mb-4 rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-xs text-rose-300">
          {simError}
        </div>
      )}

      {/* Metric Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        <div className="bg-slate-900/60 p-3 rounded-xl border border-white/5">
          <span className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold block">Current Price</span>
          <span className="text-sm font-mono-num font-bold text-slate-100">₹{stock.currentPrice.toLocaleString('en-IN')}</span>
        </div>
        <div className="bg-slate-900/60 p-3 rounded-xl border border-white/5">
          <span className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold block">Median Target ({horizonDays}D)</span>
          <span className="text-sm font-mono-num font-bold text-emerald-400">₹{simResults.finalMedian.toLocaleString('en-IN')}</span>
        </div>
        <div className="bg-slate-900/60 p-3 rounded-xl border border-white/5">
          <span className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold block">95th Percentile (Bull)</span>
          <span className="text-sm font-mono-num font-bold text-blue-400">₹{simResults.finalUpper95.toLocaleString('en-IN')}</span>
        </div>
        <div className="bg-slate-900/60 p-3 rounded-xl border border-white/5">
          <span className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold block">5th Percentile (Bear / VaR)</span>
          <span className="text-sm font-mono-num font-bold text-rose-400">₹{simResults.finalLower5.toLocaleString('en-IN')}</span>
        </div>
      </div>

      {/* Interactive Simulation Chart */}
      <div className="h-[360px] w-full relative">
        <AnimatePresence mode="wait">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" vertical={false} />
              <XAxis dataKey="day" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
              <YAxis domain={['auto', 'auto']} stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} tickFormatter={(v) => `₹${v}`} />

              <Tooltip
                content={({ active, payload }) => {
                  if (!active || !payload || !payload.length) return null;
                  const p = payload[0].payload;
                  return (
                    <div className="bg-slate-900/95 border border-white/15 p-3 rounded-xl shadow-2xl backdrop-blur-md text-xs font-mono">
                      <div className="text-slate-400 font-bold border-b border-white/10 pb-1 mb-1">
                        Timeline: {p.day}
                      </div>
                      <div className="text-emerald-400 font-bold">Median: ₹{p.median}</div>
                      <div className="text-blue-400">95th Percentile: ₹{p.p95}</div>
                      <div className="text-rose-400">5th Percentile: ₹{p.p5}</div>
                    </div>
                  );
                }}
              />

              <ReferenceLine y={stock.currentPrice} stroke="#64748b" strokeDasharray="3 3" label={{ value: 'Current', fill: '#94a3b8', fontSize: 10 }} />

              {/* Render background paths */}
              {simResults.paths.map((p, idx) => (
                <Line
                  key={p.id}
                  type="monotone"
                  dataKey={p.id}
                  stroke={idx === 0 ? '#10b981' : idx % 6 === 0 ? 'rgba(59, 130, 246, 0.4)' : 'rgba(255, 255, 255, 0.08)'}
                  strokeWidth={idx === 0 ? 1.5 : 0.8}
                  dot={false}
                  isAnimationActive={true}
                  animationDuration={800}
                />
              ))}

              {/* Key summary lines */}
              <Line type="monotone" dataKey="median" stroke="#10b981" strokeWidth={3} dot={false} name="Median Path" />
              <Line type="monotone" dataKey="p95" stroke="#3b82f6" strokeWidth={2} strokeDasharray="4 4" dot={false} name="95th Percentile" />
              <Line type="monotone" dataKey="p5" stroke="#ef4444" strokeWidth={2} strokeDasharray="4 4" dot={false} name="5th Percentile" />
            </LineChart>
          </ResponsiveContainer>
        </AnimatePresence>
      </div>
    </motion.div>
  );
};
