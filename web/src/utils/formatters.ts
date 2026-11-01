export function formatCurrency(value: number, currencySymbol = '₹'): string {
  return `${currencySymbol}${value.toLocaleString('en-IN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

export function formatPercent(value: number, showSign = true): string {
  const formatted = Math.abs(value).toFixed(2);
  if (value > 0) return `${showSign ? '+' : ''}${formatted}%`;
  if (value < 0) return `-${formatted}%`;
  return `0.00%`;
}

export function formatNumber(value: number): string {
  return value.toLocaleString('en-IN');
}
