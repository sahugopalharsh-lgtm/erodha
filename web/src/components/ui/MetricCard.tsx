import React from 'react';
import { motion } from 'framer-motion';
import { AnimatedNumber } from './AnimatedNumber';
import { TrendingUp, TrendingDown, Info } from 'lucide-react';

interface MetricCardProps {
  label: string;
  value: number;
  prefix?: string;
  suffix?: string;
  decimals?: number;
  change?: number; // optional change percentage
  changeLabel?: string;
  isRiskMetric?: boolean; // true if lower is better/risk metric
  tooltip?: string;
  icon?: React.ReactNode;
  delay?: number;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  prefix = '',
  suffix = '',
  decimals = 2,
  change,
  changeLabel,
  isRiskMetric = false,
  tooltip,
  icon,
  delay = 0,
}) => {
  // Determine positive vs negative coloring
  const isPositiveChange = change !== undefined ? change > 0 : value >= 0;
  const isGood = isRiskMetric ? !isPositiveChange : isPositiveChange;

  const valueColor = isRiskMetric
    ? 'text-rose-400'
    : change !== undefined
    ? isPositiveChange
      ? 'text-emerald-400'
      : 'text-rose-400'
    : 'text-slate-100';

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }}
      whileHover={{ y: -3, transition: { duration: 0.2 } }}
      className="glass-panel-interactive rounded-xl p-5 relative overflow-hidden group border border-white/5 hover:border-white/15"
    >
      {/* Top subtle glow bar */}
      <div 
        className={`absolute top-0 left-0 right-0 h-[2px] opacity-70 transition-all duration-300 ${
          isRiskMetric 
            ? 'bg-gradient-to-r from-transparent via-rose-500 to-transparent' 
            : change !== undefined && isPositiveChange
            ? 'bg-gradient-to-r from-transparent via-emerald-500 to-transparent'
            : 'bg-gradient-to-r from-transparent via-emerald-500/50 to-transparent'
        }`}
      />

      <div className="flex items-center justify-between mb-2">
        <span className="text-[11px] font-semibold tracking-wider text-slate-400 uppercase flex items-center gap-1.5">
          {label}
          {tooltip && (
            <span className="group/tip relative cursor-help">
              <Info className="w-3 h-3 text-slate-500 hover:text-slate-300 transition-colors" />
              <span className="pointer-events-none absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover/tip:block w-48 p-2 text-[11px] leading-tight text-slate-200 bg-slate-900/95 border border-white/10 rounded-md shadow-xl z-30">
                {tooltip}
              </span>
            </span>
          )}
        </span>
        {icon && <div className="text-slate-400 group-hover:text-emerald-400 transition-colors">{icon}</div>}
      </div>

      <div className="flex items-baseline justify-between mt-1">
        <div className={`text-2xl lg:text-3xl font-bold tracking-tight ${valueColor}`}>
          <AnimatedNumber
            value={value}
            prefix={prefix}
            suffix={suffix}
            decimals={decimals}
          />
        </div>

        {change !== undefined && (
          <div
            className={`flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-full ${
              isGood
                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
            }`}
          >
            {isPositiveChange ? (
              <TrendingUp className="w-3 h-3" />
            ) : (
              <TrendingDown className="w-3 h-3" />
            )}
            <span>
              {isPositiveChange ? '+' : ''}
              {change.toFixed(2)}%
            </span>
          </div>
        )}
      </div>

      {changeLabel && (
        <div className="mt-2 text-[11px] text-slate-500 flex items-center justify-between">
          <span>{changeLabel}</span>
        </div>
      )}
    </motion.div>
  );
};
