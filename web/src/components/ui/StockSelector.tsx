import React from 'react';
import { useStocks } from '../../hooks/useApi';
import { UNIVERSE, placeholderStock } from '../../constants';
import { ChevronDown } from 'lucide-react';

interface StockSelectorProps {
  selectedSymbol: string;
  onSelectStock: (symbol: string) => void;
}

export const StockSelector: React.FC<StockSelectorProps> = ({
  selectedSymbol,
  onSelectStock,
}) => {
  const { stocks: apiStocks } = useStocks();
  const stocks = apiStocks.length > 0 ? apiStocks : UNIVERSE.map((u) => placeholderStock(u.symbol));
  const [isOpen, setIsOpen] = React.useState(false);
  const selectedStock = stocks.find((s) => s.symbol === selectedSymbol) || stocks[0] || {
    symbol: selectedSymbol,
    name: selectedSymbol,
    sector: 'Equity',
    currentPrice: 0,
    dailyChange: 0,
  };

  return (
    <div className="relative z-30">
      {/* Selector Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-3 bg-slate-900/90 hover:bg-slate-800 border border-white/10 hover:border-white/20 rounded-xl px-4 py-2 text-left transition-all duration-200 shadow-md group cursor-pointer"
      >
        <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 font-mono font-bold text-xs">
          {selectedStock.symbol.substring(0, 3)}
        </div>

        <div>
          <div className="flex items-center gap-2">
            <span className="font-bold text-slate-100 text-sm tracking-tight">{selectedStock.symbol}</span>
            <span className={`text-xs font-mono font-semibold ${selectedStock.dailyChange >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
              {selectedStock.dailyChange >= 0 ? '+' : ''}{selectedStock.dailyChange.toFixed(2)}%
            </span>
          </div>
          <span className="text-[11px] text-slate-400 truncate max-w-[140px] block">{selectedStock.name}</span>
        </div>

        <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform duration-200 ml-2 ${isOpen ? 'rotate-180 text-emerald-400' : ''}`} />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />
          <div className="absolute top-full left-0 mt-2 w-72 bg-slate-900/95 backdrop-blur-xl border border-white/10 rounded-xl shadow-2xl p-2 z-50 animate-in fade-in zoom-in-95">
            <div className="px-3 py-1.5 text-[10px] font-semibold text-slate-400 uppercase tracking-wider border-b border-white/5 mb-1">
              Select Asset for Modelling
            </div>

            <div className="space-y-1">
              {stocks.map((stock) => {
                const isSelected = stock.symbol === selectedSymbol;
                const isPositive = stock.dailyChange >= 0;

                return (
                  <button
                    key={stock.symbol}
                    onClick={() => {
                      onSelectStock(stock.symbol);
                      setIsOpen(false);
                    }}
                    className={`w-full flex items-center justify-between p-2.5 rounded-lg text-left transition-colors cursor-pointer ${
                      isSelected ? 'bg-emerald-500/15 border border-emerald-500/30' : 'hover:bg-slate-800/80 border border-transparent'
                    }`}
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-slate-100 text-xs">{stock.symbol}</span>
                        <span className="text-[10px] text-slate-400 bg-slate-800 px-1.5 py-0.5 rounded">{stock.sector}</span>
                      </div>
                      <span className="text-[11px] text-slate-400 block truncate">{stock.name}</span>
                    </div>

                    <div className="text-right">
                      <div className="text-xs font-mono font-bold text-slate-200">₹{stock.currentPrice.toLocaleString('en-IN')}</div>
                      <div className={`text-[10px] font-mono font-semibold ${isPositive ? 'text-emerald-400' : 'text-rose-400'}`}>
                        {isPositive ? '+' : ''}{stock.dailyChange.toFixed(2)}%
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        </>
      )}
    </div>
  );
};
