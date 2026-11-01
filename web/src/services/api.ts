import {
  Stock, StockHistoryResponse, ForecastRequest, ForecastResponse,
  MonteCarloRequest, MonteCarloResponse, RiskRequest, RiskResponse,
  IPOOfferingInput, IPOAnalysisResponse, SystemHealth,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

type ConnectionListener = (isLive: boolean, health?: SystemHealth) => void;

/**
 * Real-data API client. There is deliberately NO mock fallback: if the Django
 * backend or Yahoo Finance fails, the error is surfaced to the UI.
 */
class ApiClient {
  private isLive = false;
  private lastHealthCheck: SystemHealth | null = null;
  private listeners: Set<ConnectionListener> = new Set();

  constructor() {
    this.checkHealth().catch(() => {});
    if (typeof window !== 'undefined') {
      setInterval(() => this.checkHealth().catch(() => {}), 30000);
    }
  }

  public subscribe(listener: ConnectionListener): () => void {
    this.listeners.add(listener);
    listener(this.isLive, this.lastHealthCheck || undefined);
    return () => { this.listeners.delete(listener); };
  }

  private notify() { this.listeners.forEach((fn) => fn(this.isLive, this.lastHealthCheck || undefined)); }
  public getIsLive() { return this.isLive; }
  public getLastHealth() { return this.lastHealthCheck; }

  private async request<T>(path: string, init?: RequestInit): Promise<T> {
    let res: Response;
    try {
      res = await fetch(`${API_BASE_URL}${path}`, {
        ...init,
        headers: { Accept: 'application/json', ...(init?.body ? { 'Content-Type': 'application/json' } : {}) },
      });
    } catch {
      this.isLive = false; this.notify();
      throw new Error('Cannot reach the Erodha backend. Start it with: python backend/manage.py runserver 127.0.0.1:8000');
    }
    if (!res.ok) {
      const body = await res.json().catch(() => null);
      throw new Error(body?.error || `Request failed (${res.status})`);
    }
    this.isLive = true; this.notify();
    return res.json() as Promise<T>;
  }

  public async checkHealth(): Promise<SystemHealth> {
    const t0 = performance.now();
    try {
      const res = await fetch(`${API_BASE_URL}/health`, { headers: { Accept: 'application/json' } });
      if (!res.ok) throw new Error(`status ${res.status}`);
      const data = await res.json();
      this.lastHealthCheck = { ...data, latencyMs: Math.round(performance.now() - t0) };
      this.isLive = true; this.notify();
      return this.lastHealthCheck as SystemHealth;
    } catch (e) {
      this.isLive = false; this.notify();
      throw e;
    }
  }

  public getStocks(_demo = false): Promise<Stock[]> { return this.request<Stock[]>('/stocks'); }

  public getStock(symbol: string, _demo = false): Promise<Stock> {
    return this.request<Stock>(`/stocks/${encodeURIComponent(symbol.replace(/\s+/g, ''))}`);
  }

  public getStockHistory(symbol: string, timeframe = '6M', _demo = false): Promise<StockHistoryResponse> {
    return this.request<StockHistoryResponse>(
      `/stocks/${encodeURIComponent(symbol.replace(/\s+/g, ''))}/history?timeframe=${encodeURIComponent(timeframe)}`);
  }

  public getForecast(req: ForecastRequest): Promise<ForecastResponse> {
    return this.request<ForecastResponse>('/forecast', { method: 'POST', body: JSON.stringify(req) });
  }

  public runMonteCarlo(req: MonteCarloRequest): Promise<MonteCarloResponse> {
    return this.request<MonteCarloResponse>('/simulations/monte-carlo', { method: 'POST', body: JSON.stringify(req) });
  }

  public getRiskAnalysis(req: RiskRequest): Promise<RiskResponse> {
    return this.request<RiskResponse>('/risk', { method: 'POST', body: JSON.stringify(req) });
  }

  public analyzeIPO(offering: IPOOfferingInput): Promise<IPOAnalysisResponse> {
    return this.request<IPOAnalysisResponse>('/ipo/analyze', { method: 'POST', body: JSON.stringify(offering) });
  }
}

export const api = new ApiClient();
