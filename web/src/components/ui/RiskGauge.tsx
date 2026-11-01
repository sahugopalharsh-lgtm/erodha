import React from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, ShieldCheck, ShieldAlert } from 'lucide-react';

interface RiskGaugeProps {
  score: number; // 0 to 100
  level: 'LOW' | 'MODERATE' | 'HIGH' | 'EXTREME';
  var95: string;
  maxDrawdown: string;
}

export const RiskGauge: React.FC<RiskGaugeProps> = ({
  score = 45,
  level = 'MODERATE',
  var95,
  maxDrawdown,
}) => {
  const getLevelConfig = () => {
    switch (level) {
      case 'LOW':
        return {
          color: 'text-emerald-400',
          bgGlow: 'from-emerald-500/20 to-emerald-500/0',
          borderColor: 'border-emerald-500/30',
          icon: <ShieldCheck className="w-5 h-5 text-emerald-400" />,
          label: 'LOW RISK',
          desc: 'Asset displays low tail-jump volatility and robust Sharpe ratio.'
        };
      case 'MODERATE':
        return {
          color: 'text-amber-400',
          bgGlow: 'from-amber-500/20 to-amber-500/0',
          borderColor: 'border-amber-500/30',
          icon: <AlertTriangle className="w-5 h-5 text-amber-400" />,
          label: 'MODERATE RISK',
          desc: 'Asset exhibits typical market drift with occasional jump events.'
        };
      case 'HIGH':
      case 'EXTREME':
      default:
        return {
          color: 'text-rose-400',
          bgGlow: 'from-rose-500/20 to-rose-500/0',
          borderColor: 'border-rose-500/30',
          icon: <ShieldAlert className="w-5 h-5 text-rose-400" />,
          label: 'HIGH TAIL RISK',
          desc: 'Significant risk of sudden discontinuous negative jump shocks.'
        };
    }
  };

  const config = getLevelConfig();

  return (
    <div className="glass-panel rounded-xl p-6 border border-white/5 relative overflow-hidden">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Risk Assessment Index
          </h3>
          <div className="flex items-center gap-2 mt-1">
            {config.icon}
            <span className={`text-lg font-bold ${config.color}`}>{config.label}</span>
          </div>
        </div>

        <div className="text-right">
          <span className="text-[11px] text-slate-400 uppercase tracking-wider block">Risk Score</span>
          <span className="text-2xl font-mono-num font-bold text-slate-100">{score}<span className="text-slate-500 text-sm">/100</span></span>
        </div>
      </div>

      {/* Financial Linear Gauge Bar */}
      <div className="mt-4">
        <div className="flex justify-between text-[10px] font-mono-num font-semibold text-slate-400 uppercase tracking-wider mb-2">
          <span className="text-emerald-400">LOW (0)</span>
          <span className="text-amber-400">MODERATE (50)</span>
          <span className="text-rose-400">HIGH (100)</span>
        </div>

        <div className="relative h-3 w-full bg-slate-800/80 rounded-full p-0.5 border border-white/5 overflow-hidden">
          {/* Gradient backdrop */}
          <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/40 via-amber-500/40 to-rose-500/40 opacity-70" />

          {/* Animated fill indicator */}
          <motion.div
            initial={{ width: '0%' }}
            animate={{ width: `${score}%` }}
            transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1] }}
            className="h-full bg-slate-100 rounded-full relative z-10 shadow-[0_0_12px_rgba(255,255,255,0.8)]"
          >
            <div className="absolute right-0 top-1/2 -translate-y-1/2 w-2 h-2 bg-white rounded-full shadow-[0_0_8px_rgba(255,255,255,1)]" />
          </motion.div>
        </div>
      </div>

      {/* Key Risk Metrics Pills */}
      <div className="grid grid-cols-2 gap-3 mt-6 pt-4 border-t border-white/5">
        <div className="bg-slate-900/40 p-3 rounded-lg border border-white/5">
          <span className="text-[10px] uppercase tracking-wider text-slate-400 block font-semibold">Value at Risk (95%)</span>
          <span className="text-sm font-mono-num font-semibold text-rose-400 mt-0.5 block">{var95}</span>
        </div>

        <div className="bg-slate-900/40 p-3 rounded-lg border border-white/5">
          <span className="text-[10px] uppercase tracking-wider text-slate-400 block font-semibold">Max Historical Drawdown</span>
          <span className="text-sm font-mono-num font-semibold text-rose-400 mt-0.5 block">{maxDrawdown}</span>
        </div>
      </div>
    </div>
  );
};
