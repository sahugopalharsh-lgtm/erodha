export type PageId = 
  | 'landing' 
  | 'dashboard' 
  | 'stocks' 
  | 'forecast' 
  | 'risk' 
  | 'ipo'
  | 'model' 
  | 'about';

export interface Stock {
  symbol: string;
  name: string;
  sector: string;
  currentPrice: number;
  dailyChange: number; // percentage
  dailyChangeAmount: number;
  volatility: number; // percentage e.g. 21.43
  forecastPrice: number;
  forecastChange: number; // percentage
  var95: number; // e.g. 142.80
  var99: number; // e.g. 198.40
  maxDrawdown: number; // e.g. -12.63
  sharpeRatio: number; // e.g. 1.42
  beta: number; // e.g. 1.15
  jumpFrequency: number; // jumps per year (lambda)
  meanJumpSize: number; // percentage e.g. -4.5%
  marketCap: string; // e.g. "₹19.2 Lakh Cr"
  volume: string; // e.g. "4.8M"
  description: string;
  currency?: string;
  exchange?: string;
  dataSource?: string;
  isDemo?: boolean;
  lastUpdated?: string;
}

export interface TimeSeriesDataPoint {
  date: string;
  timestamp: number;
  price: number;
  ma20?: number;
  forecast?: number;
  confidenceUpper?: number;
  confidenceLower?: number;
  isJump?: boolean;
  jumpType?: 'up' | 'down';
  type?: 'historical' | 'forecast';
}

export interface StockHistoryResponse {
  symbol: string;
  timeframe: string;
  historical: TimeSeriesDataPoint[];
  forecast: TimeSeriesDataPoint[];
  totalReturnPct: number;
  dataSource: string;
  isDemo: boolean;
  lastUpdated: string;
}

export interface PathPoint {
  day: number;
  price: number;
}

export interface MonteCarloPath {
  id: string;
  color?: string;
  data: PathPoint[];
}

export interface SummaryCurvePoint {
  day: number;
  p5: number;
  p25: number;
  median: number;
  p75: number;
  p95: number;
}

export interface MonteCarloRequest {
  symbol?: string;
  numSimulations?: number;
  horizonDays?: number;
  initialPrice?: number;
  drift?: number;
  volatility?: number;
  jumpLambda?: number;
  jumpMu?: number;
  jumpSigma?: number;
  seed?: number;
  demo?: boolean;
}

export interface MonteCarloResponse {
  symbol: string;
  initialPrice: number;
  numSimulations: number;
  horizonDays: number;
  paths: MonteCarloPath[];
  summaryCurve: SummaryCurvePoint[];
  finalMedian: number;
  finalUpper95: number;
  finalLower5: number;
  var95: number;
  var99: number;
  parametersUsed: Record<string, any>;
  disclaimer: string;
}

export interface QuantileBand {
  day: number;
  date: string;
  p5: number;
  p25: number;
  median: number;
  p75: number;
  p95: number;
}

export interface ForecastRequest {
  symbol: string;
  horizonDays?: number;
  confidenceLevel?: number;
  seed?: number;
  demo?: boolean;
}

export interface ForecastResponse {
  symbol: string;
  spotPrice: number;
  horizonDays: number;
  confidenceLevel: number;
  medianTargetPrice: number;
  expectedReturnPct: number;
  lowerBound: number;
  upperBound: number;
  annualDriftPct: number;
  annualDiffusionVolPct: number;
  jumpFrequency: number;
  meanJumpSizePct: number;
  quantileBands: QuantileBand[];
  chartSeries: TimeSeriesDataPoint[];
  disclaimer: string;
  dataSource: string;
  isDemo: boolean;
}

export interface ReturnDistributionBin {
  rangeLabel: string;
  minVal: number;
  maxVal: number;
  count: number;
  isTailRisk: boolean;
}

export interface RiskRequest {
  symbol: string;
  horizonDays?: number;
  lookbackDays?: number;
  demo?: boolean;
}

export interface RiskResponse {
  symbol: string;
  currentPrice: number;
  volatilityAnnualPct: number;
  var95Amount: number;
  var95Pct: number;
  var99Amount: number;
  var99Pct: number;
  expectedShortfall95Amount: number;
  expectedShortfall95Pct: number;
  expectedShortfall99Amount: number;
  expectedShortfall99Pct: number;
  maxDrawdownPct: number;
  sharpeRatio: number;
  beta: number;
  jumpFrequency: number;
  meanJumpSizePct: number;
  riskScore: number;
  riskLevel: 'LOW' | 'MODERATE' | 'HIGH' | 'EXTREME';
  returnDistribution: ReturnDistributionBin[];
  provenance: Record<string, any>;
  disclaimer: string;
}

export interface IPOOfferingInput {
  companyName: string;
  sector: string;
  priceBandMin: number;
  priceBandMax: number;
  lotSize: number;
  issueSizeCr: number;
  retailQuotaPct?: number;
  qibQuotaPct?: number;
  niiQuotaPct?: number;
  peRatio?: number;
  sectorPe?: number;
  revenueGrowthPct?: number;
  profitGrowthPct?: number;
  greyMarketPremium?: number;
  retailSubscriptionMultiple: number;
  qibSubscriptionMultiple?: number;
  niiSubscriptionMultiple?: number;
}

export interface ListingGainScenario {
  name: string;
  projectedListingPrice: number;
  projectedGainPct: number;
  probabilityWeight: number;
  description: string;
}

export interface IPOAnalysisResponse {
  companyName: string;
  sector: string;
  cutOffPrice: number;
  minimumInvestmentPerLot: number;
  valuationAnalysis: Record<string, any>;
  allotmentOdds: {
    retailSubscriptionMultiple: number;
    qibSubscriptionMultiple: number;
    niiSubscriptionMultiple: number;
    retailLotteryProbabilityPct: number;
    oddsRatio: string;
    description: string;
    sebiRuleNote: string;
  };
  scenarios: ListingGainScenario[];
  expectedListingGainPct: number;
  day1VaR95Amount: number;
  day1VaR95Pct: number;
  userEnteredAssumptions: Record<string, any>;
  modelAssumptions: Record<string, any>;
  disclaimer: string;
}

export interface SystemHealth {
  status: string;
  version: string;
  activeDataProvider: string;
  uptimeSeconds: number;
  serverTime?: string;
  latencyMs?: number;
}

export interface SimulationParams {
  numSimulations: number;
  horizonDays: number;
  initialPrice: number;
  drift: number; // mu (% per year)
  volatility: number; // sigma (% per year)
  jumpLambda: number; // annual jump frequency
  jumpMu: number; // mean jump magnitude (%)
  jumpSigma: number; // jump magnitude volatility (%)
}

export interface JumpModelTerm {
  symbol: string;
  name: string;
  description: string;
  role: string;
  mathDetail: string;
  color: string;
}

export interface RiskLevelInfo {
  level: 'LOW' | 'MODERATE' | 'HIGH' | 'EXTREME';
  color: string;
  description: string;
}
