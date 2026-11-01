import { Stock } from './types';

// Tickers shown in the selector. Labels only: all numbers come from the Django API.
export const UNIVERSE: { symbol: string; name: string }[] = [
  { symbol: 'RELIANCE', name: 'Reliance Industries Ltd.' },
  { symbol: 'TCS', name: 'Tata Consultancy Services Ltd.' },
  { symbol: 'INFY', name: 'Infosys Ltd.' },
  { symbol: 'HDFCBANK', name: 'HDFC Bank Ltd.' },
  { symbol: 'NIFTY 50', name: 'Nifty 50 Index' },
];

/** Empty shell shown while the real data loads. Contains no market numbers. */
export function placeholderStock(symbol: string): Stock {
  const known = UNIVERSE.find((u) => u.symbol === symbol);
  return {
    symbol, name: known?.name ?? symbol, sector: '—',
    currentPrice: 0, dailyChange: 0, dailyChangeAmount: 0, volatility: 0,
    forecastPrice: 0, forecastChange: 0, var95: 0, var99: 0, maxDrawdown: 0,
    sharpeRatio: 0, beta: 0, jumpFrequency: 0, meanJumpSize: 0,
    marketCap: '—', volume: '—', description: 'Loading live data…',
  };
}
