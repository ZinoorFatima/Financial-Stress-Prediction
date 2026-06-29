// Number formatting helpers for the dashboard.

export const fmtCurrency = (n: number): string => {
  const abs = Math.abs(n);
  const sign = n < 0 ? "-" : "";
  if (abs >= 1e9) return `${sign}$${(abs / 1e9).toFixed(2)}B`;
  if (abs >= 1e6) return `${sign}$${(abs / 1e6).toFixed(2)}M`;
  if (abs >= 1e3) return `${sign}$${(abs / 1e3).toFixed(1)}K`;
  return `${sign}$${abs.toFixed(0)}`;
};

export const fmtPct = (n: number, digits = 2): string => `${(n * 100).toFixed(digits)}%`;

export const fmtSignedCurrency = (n: number): string =>
  `${n >= 0 ? "+" : ""}${fmtCurrency(n)}`;
