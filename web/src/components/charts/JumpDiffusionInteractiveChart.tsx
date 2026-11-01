import React, { useState } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceDot,
} from 'recharts';
import { Zap, Play, CheckCircle2 } from 'lucide-react';

export const JumpDiffusionInteractiveChart: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'both' | 'traditional' | 'jump'>('both');
  const [isAnimating, setIsAnimating] = useState<boolean>(false);

  const data = [
    { t: 'T0', traditional: 100, jumpModel: 100 },
    { t: 'T1', traditional: 101, jumpModel: 101 },
    { t: 'T2', traditional: 102, jumpModel: 103 },
    { t: 'T3 (Shock)', traditional: 103, jumpModel: 78, isJump: true },
    { t: 'T4', traditional: 104, jumpModel: 80 },
    { t: 'T5', traditional: 105, jumpModel: 82 },
    { t: 'T6', traditional: 106, jumpModel: 85 },
  ];

  const triggerAnimation = () => {
    setIsAnimating(true);
    setTimeout(() => setIsAnimating(false), 1200);
  };

  return (
    <div className="glass-panel rounded-2xl p-6 border border-white/5 relative overflow-hidden shadow-xl">
      {/* Visual Component Pipeline Header */}
      <div className="mb-6 p-4 bg-slate-900/80 rounded-xl border border-white/10">
        <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest text-center mb-3">
          Jump-Diffusion Model Mechanics
        </div>

        <div className="grid grid-cols-2 md:grid-cols-7 gap-2 items-center text-center font-mono text-xs">
          <div className="bg-slate-800/80 p-2 rounded-lg border border-white/5 text-slate-200">
            <span className="text-[10px] text-slate-400 block font-sans uppercase">Drift</span>
            <span className="font-bold text-emerald-400">μ S dt</span>
          </div>

          <div className="text-slate-500 font-bold text-lg hidden md:block">+</div>

          <div className="bg-slate-800/80 p-2 rounded-lg border border-white/5 text-slate-200">
            <span className="text-[10px] text-slate-400 block font-sans uppercase">Diffusion</span>
            <span className="font-bold text-blue-400">σ S dW</span>
          </div>

          <div className="text-slate-500 font-bold text-lg hidden md:block">+</div>

          <div className="bg-rose-500/15 p-2 rounded-lg border border-rose-500/30 text-rose-300 font-bold animate-pulse">
            <span className="text-[10px] text-rose-400 block font-sans uppercase">Sudden Jump</span>
            <span className="font-bold text-rose-400">J S dN</span>
          </div>

          <div className="text-slate-500 font-bold text-lg hidden md:block">=</div>

          <div className="bg-emerald-500/15 p-2 rounded-lg border border-emerald-500/30 text-emerald-300 font-bold col-span-2 md:col-span-1">
            <span className="text-[10px] text-emerald-400 block font-sans uppercase">Model</span>
            <span className="font-bold text-emerald-400">dS</span>
          </div>
        </div>
      </div>

      {/* Selector & Action */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        <div className="flex items-center gap-2">
          <Zap className="w-5 h-5 text-rose-400" />
          <h3 className="text-lg font-bold text-slate-100">Continuous vs Discontinuous Trajectory</h3>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center bg-slate-900/90 p-1 rounded-xl border border-white/10 text-xs">
            <button
              onClick={() => setActiveTab('both')}
              className={`px-3 py-1 rounded-lg transition-colors cursor-pointer font-medium ${
                activeTab === 'both' ? 'bg-slate-700 text-white font-bold' : 'text-slate-400'
              }`}
            >
              Side-by-Side
            </button>
            <button
              onClick={() => setActiveTab('traditional')}
              className={`px-3 py-1 rounded-lg transition-colors cursor-pointer font-medium ${
                activeTab === 'traditional' ? 'bg-blue-500/20 text-blue-400 font-bold border border-blue-500/30' : 'text-slate-400'
              }`}
            >
              Traditional Smooth
            </button>
            <button
              onClick={() => setActiveTab('jump')}
              className={`px-3 py-1 rounded-lg transition-colors cursor-pointer font-medium ${
                activeTab === 'jump' ? 'bg-rose-500/20 text-rose-400 font-bold border border-rose-500/30' : 'text-slate-400'
              }`}
            >
              ERODHA Jump-Diffusion
            </button>
          </div>

          <button
            onClick={triggerAnimation}
            className="flex items-center gap-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-white/10 px-3 py-1.5 rounded-xl text-xs font-semibold cursor-pointer transition-colors"
          >
            <Play className="w-3.5 h-3.5 fill-current text-emerald-400" />
            <span>Replay Jump</span>
          </button>
        </div>
      </div>

      {/* Chart */}
      <div className="h-[300px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 20, right: 20, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
            <XAxis dataKey="t" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
            <YAxis domain={[70, 115]} stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
            <Tooltip
              content={({ active, payload }) => {
                if (!active || !payload || !payload.length) return null;
                const p = payload[0].payload;
                return (
                  <div className="bg-slate-900/95 border border-white/15 p-3 rounded-lg shadow-2xl backdrop-blur-md text-xs font-mono">
                    <div className="text-slate-400 font-bold border-b border-white/10 pb-1 mb-1">{p.t}</div>
                    {(activeTab === 'both' || activeTab === 'traditional') && (
                      <div className="text-blue-400">Traditional Gaussian: {p.traditional}</div>
                    )}
                    {(activeTab === 'both' || activeTab === 'jump') && (
                      <div className="text-rose-400 font-bold">ERODHA Jump-Diffusion: {p.jumpModel}</div>
                    )}
                    {p.isJump && (
                      <div className="text-rose-400 font-bold text-[11px] pt-1">⚡ Discontinuous Jump (-24.3%)</div>
                    )}
                  </div>
                );
              }}
            />

            {(activeTab === 'both' || activeTab === 'traditional') && (
              <Line
                type="monotone"
                dataKey="traditional"
                stroke="#3b82f6"
                strokeWidth={2.5}
                strokeDasharray="4 4"
                dot={{ r: 4, fill: '#3b82f6' }}
                name="Traditional Smooth Path"
              />
            )}

            {(activeTab === 'both' || activeTab === 'jump') && (
              <Line
                type="monotone"
                dataKey="jumpModel"
                stroke="#ef4444"
                strokeWidth={3}
                dot={{ r: 5, fill: '#ef4444' }}
                name="ERODHA Jump Path"
                isAnimationActive={!isAnimating}
              />
            )}

            <ReferenceDot x="T3 (Shock)" y={78} r={8} fill="#ef4444" stroke="#ffffff" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-4 pt-3 border-t border-white/5 text-xs text-slate-400 flex justify-between items-center">
        <span>Unlike conventional diffusion models, ERODHA accounts for sudden discontinuous movements in asset prices.</span>
        <span className="font-mono text-emerald-400 flex items-center gap-1 font-bold">
          <CheckCircle2 className="w-3.5 h-3.5" /> Jump-Poisson Verified
        </span>
      </div>
    </div>
  );
};
