import { MonteCarloPath, SimulationParams, TimeSeriesDataPoint } from '../types';

// Standard normal distribution sampler using Box-Muller transform
export function randomNormal(mean = 0, stdDev = 1): number {
  let u1 = 0, u2 = 0;
  while (u1 === 0) u1 = Math.random();
  while (u2 === 0) u2 = Math.random();
  const z0 = Math.sqrt(-2.0 * Math.log(u1)) * Math.cos(2.0 * Math.PI * u2);
  return z0 * stdDev + mean;
}

// Poisson arrival sampler for jumps
export function randomPoisson(lambda: number): number {
  const L = Math.exp(-lambda);
  let k = 0;
  let p = 1;
  do {
    k++;
    p *= Math.random();
  } while (p > L);
  return k - 1;
}

/**
 * Generate a single Jump-Diffusion path using Merton's Jump-Diffusion Model:
 * dS = mu*S*dt + sigma*S*dW + J*S*dN
 */
export function generateJumpDiffusionPath(
  params: SimulationParams,
  seedRandom = false
): { day: number; price: number }[] {
  const { initialPrice, horizonDays, drift, volatility, jumpLambda, jumpMu, jumpSigma } = params;
  const dt = 1 / 252; // Daily time step in years
  const path: { day: number; price: number }[] = [{ day: 0, price: initialPrice }];

  let currentPrice = initialPrice;

  // Annualized parameters to daily scale
  const dailyDrift = (drift - 0.5 * Math.pow(volatility, 2)) * dt;
  const dailyVol = volatility * Math.sqrt(dt);
  const dailyLambda = jumpLambda * dt;

  for (let day = 1; day <= horizonDays; day++) {
    // 1. Continuous Diffusion (Brownian Motion)
    const z = seedRandom ? (Math.sin(day * 0.7) + Math.cos(day * 0.3)) * 0.7 : randomNormal(0, 1);
    const continuousReturn = dailyDrift + dailyVol * z;

    // 2. Discontinuous Jump (Poisson process)
    let jumpReturn = 0;
    const numJumps = seedRandom ? (day % 18 === 0 ? 1 : 0) : randomPoisson(dailyLambda);
    if (numJumps > 0) {
      for (let j = 0; j < numJumps; j++) {
        const jumpVal = seedRandom 
          ? (day % 36 === 0 ? -0.05 : 0.04) 
          : randomNormal(jumpMu, jumpSigma);
        jumpReturn += jumpVal;
      }
    }

    // Combine geometric diffusion + jump return
    currentPrice = currentPrice * Math.exp(continuousReturn + jumpReturn);
    currentPrice = Math.max(currentPrice, initialPrice * 0.1); // Prevent negative prices

    path.push({ day, price: Number(currentPrice.toFixed(2)) });
  }

  return path;
}

/**
 * Run Monte Carlo Simulation with N paths
 */
export function runMonteCarloSimulation(params: SimulationParams) {
  const numPathsToDisplay = Math.min(params.numSimulations, 40);
  const displayedPaths: MonteCarloPath[] = [];

  const allFinalPrices: number[] = [];
  const dailyPathsData: number[][] = Array.from({ length: params.horizonDays + 1 }, () => []);

  for (let i = 0; i < params.numSimulations; i++) {
    const rawPath = generateJumpDiffusionPath(params);
    
    // Store daily prices for percentiles calculation
    rawPath.forEach((p, dayIdx) => {
      dailyPathsData[dayIdx].push(p.price);
    });

    allFinalPrices.push(rawPath[rawPath.length - 1].price);

    if (i < numPathsToDisplay) {
      displayedPaths.push({
        id: `sim-path-${i}`,
        data: rawPath,
        color: i === 0 ? '#10b981' : i % 5 === 0 ? '#3b82f6' : 'rgba(255, 255, 255, 0.15)'
      });
    }
  }

  // Calculate Median, 95th Percentile, 5th Percentile path curves
  const summaryCurve = dailyPathsData.map((prices, day) => {
    const sorted = [...prices].sort((a, b) => a - b);
    const len = sorted.length;
    const p5 = sorted[Math.floor(len * 0.05)];
    const p25 = sorted[Math.floor(len * 0.25)];
    const p50 = sorted[Math.floor(len * 0.50)];
    const p75 = sorted[Math.floor(len * 0.75)];
    const p95 = sorted[Math.floor(len * 0.95)];

    return {
      day,
      p5: Number(p5.toFixed(2)),
      p25: Number(p25.toFixed(2)),
      median: Number(p50.toFixed(2)),
      p75: Number(p75.toFixed(2)),
      p95: Number(p95.toFixed(2)),
    };
  });

  // Sort final prices for VaR computation
  allFinalPrices.sort((a, b) => a - b);
  const initial = params.initialPrice;
  const p5Final = allFinalPrices[Math.floor(allFinalPrices.length * 0.05)];
  const p1Final = allFinalPrices[Math.floor(allFinalPrices.length * 0.01)];

  const var95 = Math.max(0, Number((initial - p5Final).toFixed(2)));
  const var99 = Math.max(0, Number((initial - p1Final).toFixed(2)));

  return {
    paths: displayedPaths,
    summaryCurve,
    finalMedian: summaryCurve[summaryCurve.length - 1].median,
    finalUpper95: summaryCurve[summaryCurve.length - 1].p95,
    finalLower5: summaryCurve[summaryCurve.length - 1].p5,
    var95,
    var99
  };
}

/**
 * Generate realistic historical stock time-series data with occasional jumps
 */
export function generateHistoricalData(
  symbol: string,
  basePrice: number,
  days = 180,
  volatilityPct = 21.43
): { historical: TimeSeriesDataPoint[]; forecast: TimeSeriesDataPoint[] } {
  const historical: TimeSeriesDataPoint[] = [];
  const forecast: TimeSeriesDataPoint[] = [];

  const now = new Date('2026-09-24');
  let currentPrice = basePrice * 0.78; // start lower 180 days ago
  const dailyVol = (volatilityPct / 100) / Math.sqrt(252);
  const dailyDrift = 0.12 / 252; // positive long-term drift

  const prices: number[] = [];

  for (let i = days; i >= 0; i--) {
    const d = new Date(now);
    d.setDate(d.getDate() - i);
    const dateStr = d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });

    // Seeded random walk for consistent smooth rendering
    const noise = Math.sin(i * 0.35) * 0.8 + (Math.cos(i * 0.15) * 0.5);
    let jump = 0;
    let isJump = false;
    let jumpType: 'up' | 'down' | undefined = undefined;

    // Simulate 2 distinct historical jump events
    if (i === 120) {
      jump = -0.075; // -7.5% earnings shock
      isJump = true;
      jumpType = 'down';
    } else if (i === 45) {
      jump = 0.068; // +6.8% regulatory clearance jump
      isJump = true;
      jumpType = 'up';
    }

    const ret = dailyDrift + dailyVol * noise + jump;
    currentPrice = Math.max(10, currentPrice * (1 + ret));
    
    // Last day matches exact base price
    if (i === 0) {
      currentPrice = basePrice;
    }

    prices.push(currentPrice);

    // Calculate 20-day Simple Moving Average
    let ma20: number | undefined = undefined;
    if (prices.length >= 20) {
      const last20 = prices.slice(prices.length - 20);
      const sum = last20.reduce((acc, val) => acc + val, 0);
      ma20 = Number((sum / 20).toFixed(2));
    }

    historical.push({
      date: dateStr,
      timestamp: d.getTime(),
      price: Number(currentPrice.toFixed(2)),
      ma20,
      isJump,
      jumpType
    });
  }

  // Generate 30-day forecast with confidence interval bands
  let forecastPrice = basePrice;
  const forecastVol = dailyVol * 1.1;

  for (let i = 1; i <= 30; i++) {
    const d = new Date(now);
    d.setDate(d.getDate() + i);
    const dateStr = d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });

    const expectedDrift = 0.15 / 252;
    forecastPrice = forecastPrice * (1 + expectedDrift + Math.sin(i * 0.2) * 0.003);

    const timeFactor = Math.sqrt(i);
    const upperBand = forecastPrice * (1 + forecastVol * timeFactor * 1.645); // 90% confidence
    const lowerBand = forecastPrice * (1 - forecastVol * timeFactor * 1.645);

    forecast.push({
      date: dateStr,
      timestamp: d.getTime(),
      price: Number(basePrice.toFixed(2)), // for baseline reference
      forecast: Number(forecastPrice.toFixed(2)),
      confidenceUpper: Number(upperBand.toFixed(2)),
      confidenceLower: Number(lowerBand.toFixed(2))
    });
  }

  return { historical, forecast };
}

/**
 * Return distribution histogram generator for Left Tail risk assessment
 */
export function generateReturnDistribution() {
  const bins: { range: string; frequency: number; isTailRisk: boolean; returnVal: number }[] = [];
  const mean = 0.05;
  const stdDev = 1.8;

  // Generate skewed distribution with fat left tail (leptokurtic jump-diffusion characteristic)
  for (let r = -6.0; r <= 6.0; r += 0.5) {
    const isTailRisk = r <= -2.5;
    
    // Normal Gaussian formula
    let freq = Math.floor(100 * Math.exp(-Math.pow(r - mean, 2) / (2 * Math.pow(stdDev, 2))));

    // Add fat-tail jump bump at -4.0% to -2.5%
    if (r <= -3.0 && r >= -4.5) {
      freq += 14; 
    }

    bins.push({
      range: `${r > 0 ? '+' : ''}${r.toFixed(1)}%`,
      frequency: Math.max(1, freq),
      isTailRisk,
      returnVal: r
    });
  }

  return bins;
}
