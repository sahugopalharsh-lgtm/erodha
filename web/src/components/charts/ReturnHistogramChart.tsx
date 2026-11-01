import React, { useMemo } from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
  ReferenceLine,
} from 'recharts';
import { ReturnDistributionBin } from '../../types';
import { AlertTriangle } from 'lucide-react';
import { motion } from 'framer-motion';

interface ReturnHistogramChartProps {
  distribution?: ReturnDistributionBin[];
}

export const ReturnHistogramChart: React.FC<ReturnHistogramChartProps> = ({ distribution }) => {
  const data = useMemo(() => {
    if (distribution && distribution.length > 0) {
      return distribution.map((bin) => ({
        range: bin.rangeLabel,
        frequency: bin.count,
        isTailRisk: bin.isTailRisk,
      }));
    }
    return [];
  }, [distribution]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="glass-panel rounded-2xl p-6 border border-white/5 relative overflow-hidden shadow-xl"
    >
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-slate-100">Simulated Return Distribution & Fat-Tail Analysis</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Empirical probability density of projected daily returns incorporating Merton Jump-Diffusion parameters.
          </p>
        </div>

        <div className="flex items-center gap-3 text-xs font-mono">
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-rose-500/10 border border-rose-500/20 text-rose-400">
            <span className="w-2 h-2 rounded-full bg-rose-500 animate-pulse" />
            <span className="font-semibold">Left-Tail Jump Risk (&lt; -2.5%)</span>
          </div>
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
            <span className="w-2 h-2 rounded-full bg-emerald-500" />
            <span className="font-semibold">Diffusion Region</span>
          </div>
        </div>
      </div>

      <div className="h-[280px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <XAxis dataKey="range" stroke="#64748b" fontSize={10} tickLine={false} axisLine={false} />
            <YAxis stroke="#64748b" fontSize={10} tickLine={false} axisLine={false} />
            <Tooltip
              content={({ active, payload }) => {
                if (!active || !payload || !payload.length) return null;
                const p = payload[0].payload;
                return (
                  <div className="bg-slate-900/95 border border-white/15 p-3 rounded-lg shadow-2xl backdrop-blur-md font-mono text-xs">
                    <div className="text-slate-300 font-bold border-b border-white/10 pb-1 mb-1">
                      Return Bin: {p.range}
                    </div>
                    <div className="text-slate-100">Simulated Frequency: {p.frequency} paths</div>
                    {p.isTailRisk && (
                      <div className="text-rose-400 font-bold text-[11px] mt-1 flex items-center gap-1">
                        <AlertTriangle className="w-3 h-3" />
                        Leptokurtic Left-Tail Jump Risk
                      </div>
                    )}
                  </div>
                );
              }}
            />
            <ReferenceLine x="0.0%" stroke="#64748b" strokeDasharray="3 3" />
            <Bar dataKey="frequency" radius={[4, 4, 0, 0]}>
              {data.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.isTailRisk ? '#ef4444' : '#10b981'}
                  fillOpacity={entry.isTailRisk ? 0.9 : 0.6}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Explanation callout */}
      <div className="mt-4 p-3.5 bg-rose-500/10 border border-rose-500/20 rounded-xl flex items-start gap-3 text-xs text-rose-300">
        <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
        <div>
          <span className="font-bold block text-rose-200">Asymmetric Fat-Tail Risk Insight:</span>
          "Extreme negative returns can contribute disproportionately to portfolio risk. Conventional Gaussian Black-Scholes models underestimate these left-tail shock events, which ERODHA models explicitly."
        </div>
      </div>
    </motion.div>
  );
};
