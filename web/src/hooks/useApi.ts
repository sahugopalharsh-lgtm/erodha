import { useState, useEffect, useCallback } from 'react';
import { api } from '../services/api';
import {
  Stock,
  StockHistoryResponse,
  ForecastResponse,
  MonteCarloResponse,
  RiskResponse,
  SystemHealth,
} from '../types';
import { placeholderStock } from '../constants';

export function useBackendStatus() {
  const [isLive, setIsLive] = useState<boolean>(() => api.getIsLive());
  const [health, setHealth] = useState<SystemHealth | null>(() => api.getLastHealth());
  const [checking, setChecking] = useState<boolean>(false);

  useEffect(() => {
    const unsubscribe = api.subscribe((live, h) => {
      setIsLive(live);
      if (h) setHealth(h);
    });
    return unsubscribe;
  }, []);

  const refresh = useCallback(async () => {
    setChecking(true);
    try {
      const h = await api.checkHealth();
      setHealth(h);
      setIsLive(true);
    } catch {
      setIsLive(false);
    } finally {
      setChecking(false);
    }
  }, []);

  return { isLive, health, checking, refresh };
}

export function useStock(symbol: string) {
  const [stock, setStock] = useState<Stock>(() => placeholderStock(symbol));
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    api.getStock(symbol)
      .then((data) => {
        if (!cancelled) {
          setStock(data);
          setError(null);
        }
      })
      .catch((err: any) => {
        if (!cancelled) setError(err?.message || 'Failed to fetch stock data');
      });

    return () => {
      cancelled = true;
    };
  }, [symbol]);

  const reload = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getStock(symbol);
      setStock(data);
    } catch (err: any) {
      setError(err?.message || 'Failed to fetch stock data');
    } finally {
      setLoading(false);
    }
  }, [symbol]);

  return { stock, loading, error, reload };
}

export function useStocks() {
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    api.getStocks()
      .then((data) => {
        if (!cancelled) {
          setStocks(data);
          setError(null);
        }
      })
      .catch((err: any) => {
        if (!cancelled) setError(err?.message || 'Failed to fetch stocks');
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const reload = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getStocks();
      setStocks(data);
    } catch (err: any) {
      setError(err?.message || 'Failed to fetch stocks');
    } finally {
      setLoading(false);
    }
  }, []);

  return { stocks, loading, error, reload };
}

export function useStockHistory(symbol: string, timeframe: string = '6M') {
  const [data, setData] = useState<StockHistoryResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    api.getStockHistory(symbol, timeframe)
      .then((res) => {
        if (!cancelled) {
          setData(res);
          setError(null);
        }
      })
      .catch((err: any) => {
        if (!cancelled) setError(err?.message || 'Failed to load historical series');
      });

    return () => {
      cancelled = true;
    };
  }, [symbol, timeframe]);

  const reload = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getStockHistory(symbol, timeframe);
      setData(res);
    } catch (err: any) {
      setError(err?.message || 'Failed to load historical series');
    } finally {
      setLoading(false);
    }
  }, [symbol, timeframe]);

  return { data, loading, error, reload };
}

export function useForecast(symbol: string, horizonDays: number = 30) {
  const [forecast, setForecast] = useState<ForecastResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    api.getForecast({ symbol, horizonDays })
      .then((res) => {
        if (!cancelled) {
          setForecast(res);
          setError(null);
        }
      })
      .catch((err: any) => {
        if (!cancelled) setError(err?.message || 'Failed to generate forecast');
      });

    return () => {
      cancelled = true;
    };
  }, [symbol, horizonDays]);

  const reload = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getForecast({ symbol, horizonDays });
      setForecast(res);
    } catch (err: any) {
      setError(err?.message || 'Failed to generate forecast');
    } finally {
      setLoading(false);
    }
  }, [symbol, horizonDays]);

  return { forecast, loading, error, reload };
}

export function useRisk(symbol: string, horizonDays: number = 1) {
  const [risk, setRisk] = useState<RiskResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    api.getRiskAnalysis({ symbol, horizonDays })
      .then((res) => {
        if (!cancelled) {
          setRisk(res);
          setError(null);
        }
      })
      .catch((err: any) => {
        if (!cancelled) setError(err?.message || 'Failed to load risk analytics');
      });

    return () => {
      cancelled = true;
    };
  }, [symbol, horizonDays]);

  const reload = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getRiskAnalysis({ symbol, horizonDays });
      setRisk(res);
    } catch (err: any) {
      setError(err?.message || 'Failed to load risk analytics');
    } finally {
      setLoading(false);
    }
  }, [symbol, horizonDays]);

  return { risk, loading, error, reload };
}

export function useMonteCarlo(symbol: string, numSimulations: number = 35, horizonDays: number = 30) {
  const [simulation, setSimulation] = useState<MonteCarloResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    api.runMonteCarlo({ symbol, numSimulations, horizonDays })
      .then((res) => {
        if (!cancelled) {
          setSimulation(res);
          setError(null);
        }
      })
      .catch((err: any) => {
        if (!cancelled) setError(err?.message || 'Simulation execution failed');
      });

    return () => {
      cancelled = true;
    };
  }, [symbol, numSimulations, horizonDays]);

  const reload = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.runMonteCarlo({ symbol, numSimulations, horizonDays });
      setSimulation(res);
    } catch (err: any) {
      setError(err?.message || 'Simulation execution failed');
    } finally {
      setLoading(false);
    }
  }, [symbol, numSimulations, horizonDays]);

  return { simulation, loading, error, reload };
}
