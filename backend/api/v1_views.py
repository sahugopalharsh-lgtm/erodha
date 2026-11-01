"""
Erodha /api/v1 adapter
======================
Serves the React dashboard using the REAL quant_engine (GBM / Merton MLE /
Monte Carlo / VaR / ES). Nothing here is mocked: if market data cannot be
fetched the endpoint returns an error and the UI shows it.

Response field names match legacy_prototype/src/types/index.ts (camelCase).
"""

import time
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import yfinance as yf
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.market_data_service import fetch_historical_prices
from quant_engine.estimation import estimate_merton_mle
from quant_engine.ipo_analysis import IPOMarketData, analyze_ipo
from quant_engine.monte_carlo import run_monte_carlo_forecast
from quant_engine.risk import (
    calculate_maximum_drawdown,
    compute_empirical_var_es,
    horizon_returns_from_daily,
)

DISCLAIMER = (
    "Scenario analysis from a calibrated stochastic model, not a price prediction "
    "or investment advice. Past statistics do not guarantee future behaviour."
)

UNIVERSE = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "NIFTY 50"]
_ALIASES = {"NIFTY50": "^NSEI", "NIFTY": "^NSEI", "NSEI": "^NSEI", "SENSEX": "^BSESN"}
BENCHMARK = "^NSEI"
_TF_DAYS = {"1D": 5, "1W": 10, "1M": 22, "3M": 66, "6M": 126, "1Y": 252, "5Y": 1260}

_TTL = 15 * 60
_cache = {}


def _cached(key, fn):
    now = time.time()
    hit = _cache.get(key)
    if hit and now - hit[0] < _TTL:
        return hit[1]
    val = fn()
    _cache[key] = (now, val)
    return val


def yf_symbol(raw: str) -> str:
    s = raw.strip().upper().replace(" ", "")
    if s in _ALIASES:
        return _ALIASES[s]
    if "." in s or s.startswith("^"):
        return s
    return s + ".NS"


def _market(symbol: str, period: str = "5y"):
    ysym = yf_symbol(symbol)
    return _cached(("px", ysym, period), lambda: fetch_historical_prices(ysym, period))


def _calib(symbol: str):
    ysym = yf_symbol(symbol)

    def build():
        prices, rets, _, synth = _market(symbol)
        return estimate_merton_mle(rets, symbol=ysym), synth

    return _cached(("cal", ysym), build)


def _info(symbol: str) -> dict:
    ysym = yf_symbol(symbol)

    def get():
        try:
            return yf.Ticker(ysym).info or {}
        except Exception:
            return {}

    return _cached(("info", ysym), get)


def _forecast(symbol, horizon_days, n_paths=3000, seed=42, calib=None, s0=None):
    prices, _, _, _ = _market(symbol)
    p = calib or _calib(symbol)[0]
    s0 = float(prices.iloc[-1]) if s0 is None else s0
    fc = run_monte_carlo_forecast(
        model="MERTON", s0=s0, mu=p.mu_merton, sigma=p.sigma_continuous,
        lam=p.lam, m_j=p.m_j, delta_j=p.delta_j,
        horizon_days=horizon_days, n_steps=horizon_days, n_paths=n_paths, seed=seed,
    )
    return fc, prices, p


def _future_dates(last, n):
    return list(pd.bdate_range(start=last + pd.Timedelta(days=1), periods=n))


def _fmt_cap(info) -> str:
    cap = info.get("marketCap")
    if not cap:
        return "—"
    if info.get("currency") == "INR":
        return f"₹{cap / 1e12:.2f} Lakh Cr"
    return f"{info.get('currency', '$')} {cap / 1e9:.1f} B"


def _fmt_vol(info) -> str:
    v = info.get("averageVolume") or info.get("volume")
    return f"{v / 1e6:.2f} M" if v else "—"


def _error(exc, code=status.HTTP_502_BAD_GATEWAY):
    return Response({"error": str(exc)}, status=code)


def build_stock(symbol: str) -> dict:
    prices, rets, _, synth = _market(symbol)
    params, _ = _calib(symbol)
    info = _info(symbol)
    st = rets.stats
    last, prev = float(prices.iloc[-1]), float(prices.iloc[-2])
    daily_pct = (last / prev - 1) * 100

    daily = rets.simple_returns.values
    v95 = compute_empirical_var_es(daily, 0.95).var_percentage
    v99 = compute_empirical_var_es(daily, 0.99).var_percentage

    beta = 1.0 if yf_symbol(symbol) == BENCHMARK else 0.0
    if yf_symbol(symbol) != BENCHMARK:
        try:
            _, b_rets, _, _ = _market(BENCHMARK)
            joined = pd.concat([rets.simple_returns, b_rets.simple_returns], axis=1, join="inner").dropna()
            if len(joined) > 60:
                beta = float(np.cov(joined.iloc[:, 0], joined.iloc[:, 1])[0, 1] / np.var(joined.iloc[:, 1], ddof=1))
        except Exception:
            pass

    fc, _, _ = _forecast(symbol, 30, n_paths=2000, calib=params)
    ysym = yf_symbol(symbol)
    return {
        "symbol": symbol.strip().upper(),
        "name": info.get("longName") or info.get("shortName") or ysym,
        "sector": info.get("sector") or info.get("quoteType") or "—",
        "currentPrice": round(last, 2),
        "dailyChange": round(daily_pct, 2),
        "dailyChangeAmount": round(last - prev, 2),
        "volatility": round(st.annualized_volatility * 100, 2),
        "forecastPrice": round(fc.terminal_median, 2),
        "forecastChange": round((fc.terminal_median / last - 1) * 100, 2),
        "var95": round(last * v95, 2),
        "var99": round(last * v99, 2),
        "maxDrawdown": round(-calculate_maximum_drawdown(prices.values) * 100, 2),
        "sharpeRatio": round(st.arithmetic_annualized_return / st.annualized_volatility, 2)
        if st.annualized_volatility > 0 else 0.0,
        "beta": round(beta, 2),
        "jumpFrequency": round(params.lam, 2),
        "meanJumpSize": round(params.m_j * 100, 2),
        "marketCap": _fmt_cap(info),
        "volume": _fmt_vol(info),
        "description": (info.get("longBusinessSummary") or "")[:300],
        "currency": info.get("currency", "INR"),
        "exchange": info.get("exchange", "NSE"),
        "dataSource": "yfinance" if not synth else "synthetic",
        "isDemo": bool(synth),
        "lastUpdated": datetime.now(timezone.utc).isoformat(),
    }


class StocksView(APIView):
    def get(self, request):
        out, errors = [], []
        for sym in UNIVERSE:
            try:
                out.append(_cached(("stock", sym), lambda s=sym: build_stock(s)))
            except Exception as exc:  # keep the list usable if one ticker fails
                errors.append(f"{sym}: {exc}")
        if not out:
            return _error("; ".join(errors))
        return Response(out)


class StockDetailView(APIView):
    def get(self, request, symbol):
        try:
            return Response(_cached(("stock", symbol.upper()), lambda: build_stock(symbol)))
        except Exception as exc:
            return _error(exc)


class StockHistoryView(APIView):
    def get(self, request, symbol):
        tf = request.query_params.get("timeframe", "6M").upper()
        n = _TF_DAYS.get(tf, 126)
        try:
            prices, rets, _, synth = _market(symbol)
            params, _ = _calib(symbol)
            ma20 = prices.rolling(20).mean()
            log_r = rets.log_returns
            med = float(np.median(log_r.values))
            cut = 3.0 * 1.4826 * float(np.median(np.abs(log_r.values - med)))
            tail = prices.iloc[-n:]
            hist = []
            for ts, px in tail.items():
                lr = log_r.get(ts, np.nan)
                is_jump = bool(np.isfinite(lr) and abs(lr - med) > cut)
                pt = {
                    "date": ts.strftime("%Y-%m-%d"),
                    "timestamp": int(ts.timestamp() * 1000),
                    "price": round(float(px), 2),
                    "isJump": is_jump,
                    "type": "historical",
                }
                if np.isfinite(ma20.get(ts, np.nan)):
                    pt["ma20"] = round(float(ma20[ts]), 2)
                if is_jump:
                    pt["jumpType"] = "up" if lr > med else "down"
                hist.append(pt)

            fc, _, _ = _forecast(symbol, 30, calib=params)
            dates = _future_dates(prices.index[-1], 30)
            fpts = []
            for i, d in enumerate(dates, start=1):
                fpts.append({
                    "date": d.strftime("%Y-%m-%d"),
                    "timestamp": int(d.timestamp() * 1000),
                    "price": round(float(fc.median_path[i]), 2),
                    "forecast": round(float(fc.median_path[i]), 2),
                    "confidenceUpper": round(float(fc.q95_path[i]), 2),
                    "confidenceLower": round(float(fc.q05_path[i]), 2),
                    "type": "forecast",
                })
            total_ret = (float(tail.iloc[-1]) / float(tail.iloc[0]) - 1) * 100
            return Response({
                "symbol": symbol.upper(), "timeframe": tf,
                "historical": hist, "forecast": fpts,
                "totalReturnPct": round(total_ret, 2),
                "dataSource": "yfinance" if not synth else "synthetic",
                "isDemo": bool(synth),
                "lastUpdated": datetime.now(timezone.utc).isoformat(),
            })
        except Exception as exc:
            return _error(exc)


class ForecastV1View(APIView):
    def post(self, request):
        d = request.data
        symbol = d.get("symbol", "RELIANCE")
        horizon = int(d.get("horizonDays", 30))
        conf = float(d.get("confidenceLevel", 0.90))
        seed = int(d.get("seed", 42))
        if not 1 <= horizon <= 1260:
            return _error("horizonDays must be between 1 and 1260", status.HTTP_400_BAD_REQUEST)
        try:
            fc, prices, p = _forecast(symbol, horizon, n_paths=5000, seed=seed)
            _, _, _, synth = _market(symbol)
            s0 = fc.s0
            lo_q, hi_q = (1 - conf) / 2 * 100, (1 + conf) / 2 * 100
            lower = float(np.percentile(fc.terminal_prices, lo_q))
            upper = float(np.percentile(fc.terminal_prices, hi_q))
            dates = _future_dates(prices.index[-1], horizon)
            bands, series = [], []
            for i, dt in enumerate(dates, start=1):
                ds = dt.strftime("%Y-%m-%d")
                bands.append({
                    "day": i, "date": ds,
                    "p5": round(float(fc.q05_path[i]), 2), "p25": round(float(fc.q25_path[i]), 2),
                    "median": round(float(fc.median_path[i]), 2),
                    "p75": round(float(fc.q75_path[i]), 2), "p95": round(float(fc.q95_path[i]), 2),
                })
                series.append({
                    "date": ds, "timestamp": int(dt.timestamp() * 1000),
                    "price": round(float(fc.median_path[i]), 2),
                    "forecast": round(float(fc.median_path[i]), 2),
                    "confidenceUpper": round(float(fc.q95_path[i]), 2),
                    "confidenceLower": round(float(fc.q05_path[i]), 2),
                    "type": "forecast",
                })
            return Response({
                "symbol": symbol.upper(), "spotPrice": round(s0, 2), "horizonDays": horizon,
                "confidenceLevel": conf,
                "medianTargetPrice": round(fc.terminal_median, 2),
                "expectedReturnPct": round((fc.terminal_mean / s0 - 1) * 100, 2),
                "lowerBound": round(lower, 2), "upperBound": round(upper, 2),
                "annualDriftPct": round(p.mu_merton * 100, 2),
                "annualDiffusionVolPct": round(p.sigma_continuous * 100, 2),
                "jumpFrequency": round(p.lam, 2),
                "meanJumpSizePct": round(p.m_j * 100, 2),
                "quantileBands": bands, "chartSeries": series,
                "disclaimer": DISCLAIMER,
                "dataSource": "yfinance" if not synth else "synthetic",
                "isDemo": bool(synth),
            })
        except Exception as exc:
            return _error(exc)


class MonteCarloV1View(APIView):
    def post(self, request):
        d = request.data
        symbol = d.get("symbol", "RELIANCE")
        n_sims = int(d.get("numSimulations", 1000))
        horizon = int(d.get("horizonDays", 30))
        seed = int(d.get("seed", 42))
        if not (1 <= horizon <= 1260 and 10 <= n_sims <= 50000):
            return _error("horizonDays 1-1260 and numSimulations 10-50000 required", status.HTTP_400_BAD_REQUEST)
        try:
            p = _calib(symbol)[0]
            prices, _, _, _ = _market(symbol)
            s0 = float(d["initialPrice"]) if d.get("initialPrice") is not None else float(prices.iloc[-1])
            mu = float(d["drift"]) if d.get("drift") is not None else p.mu_merton
            sigma = float(d["volatility"]) if d.get("volatility") is not None else p.sigma_continuous
            lam = float(d["jumpLambda"]) if d.get("jumpLambda") is not None else p.lam
            m_j = float(d["jumpMu"]) if d.get("jumpMu") is not None else p.m_j
            dj = float(d["jumpSigma"]) if d.get("jumpSigma") is not None else p.delta_j
            fc = run_monte_carlo_forecast(
                model="MERTON", s0=s0, mu=mu, sigma=sigma, lam=lam, m_j=m_j, delta_j=dj,
                horizon_days=horizon, n_steps=horizon, n_paths=n_sims, seed=seed,
                n_sample_trajectories=30,
            )
            paths = [
                {"id": f"path-{i}", "data": [{"day": k, "price": round(float(v), 2)} for k, v in enumerate(col)]}
                for i, col in enumerate(fc.sample_paths.T)
            ]
            curve = [
                {"day": k, "p5": round(float(fc.q05_path[k]), 2), "p25": round(float(fc.q25_path[k]), 2),
                 "median": round(float(fc.median_path[k]), 2), "p75": round(float(fc.q75_path[k]), 2),
                 "p95": round(float(fc.q95_path[k]), 2)}
                for k in range(horizon + 1)
            ]
            return Response({
                "symbol": symbol.upper(), "initialPrice": round(s0, 2),
                "numSimulations": n_sims, "horizonDays": horizon,
                "paths": paths, "summaryCurve": curve,
                "finalMedian": round(fc.terminal_median, 2),
                "finalUpper95": round(fc.terminal_q95, 2),
                "finalLower5": round(fc.terminal_q05, 2),
                "var95": round(s0 - fc.terminal_q05, 2),
                "var99": round(s0 - float(np.percentile(fc.terminal_prices, 1)), 2),
                "parametersUsed": {"mu": mu, "sigma": sigma, "lambda": lam, "m_j": m_j,
                                   "delta_j": dj, "seed": seed, "model": "Merton jump-diffusion"},
                "disclaimer": DISCLAIMER,
            })
        except Exception as exc:
            return _error(exc)


class RiskV1View(APIView):
    def post(self, request):
        d = request.data
        symbol = d.get("symbol", "RELIANCE")
        horizon = int(d.get("horizonDays", 1))
        lookback = int(d.get("lookbackDays", 504))
        try:
            prices, rets, _, _ = _market(symbol)
            p = _calib(symbol)[0]
            daily = rets.simple_returns.values[-lookback:]
            hret = horizon_returns_from_daily(daily, horizon)
            s0 = float(prices.iloc[-1])
            m95 = compute_empirical_var_es(hret, 0.95, s0, horizon)
            m99 = compute_empirical_var_es(hret, 0.99, s0, horizon)

            fc, _, _ = _forecast(symbol, max(horizon, 1), n_paths=20000, calib=p)
            mc = fc.terminal_prices / s0 - 1.0
            mc95 = compute_empirical_var_es(mc, 0.95, s0, horizon)

            counts, edges = np.histogram(hret * 100, bins=24)
            thr = -m95.var_percentage * 100
            dist = [{
                "rangeLabel": f"{edges[i]:.1f}%",
                "minVal": round(float(edges[i]), 3), "maxVal": round(float(edges[i + 1]), 3),
                "count": int(counts[i]), "isTailRisk": bool(edges[i + 1] <= thr),
            } for i in range(len(counts))]

            st = rets.stats
            vol = st.annualized_volatility * 100
            score = int(min(100, round(vol * 2)))
            level = "LOW" if vol < 15 else "MODERATE" if vol < 25 else "HIGH" if vol < 40 else "EXTREME"
            stock = _cached(("stock", symbol.upper()), lambda: build_stock(symbol))
            return Response({
                "symbol": symbol.upper(), "currentPrice": round(s0, 2),
                "volatilityAnnualPct": round(vol, 2),
                "var95Amount": round(m95.var_amount, 2), "var95Pct": round(m95.var_percentage * 100, 3),
                "var99Amount": round(m99.var_amount, 2), "var99Pct": round(m99.var_percentage * 100, 3),
                "expectedShortfall95Amount": round(m95.es_amount, 2),
                "expectedShortfall95Pct": round(m95.es_percentage * 100, 3),
                "expectedShortfall99Amount": round(m99.es_amount, 2),
                "expectedShortfall99Pct": round(m99.es_percentage * 100, 3),
                "maxDrawdownPct": round(-calculate_maximum_drawdown(prices.values) * 100, 2),
                "sharpeRatio": stock["sharpeRatio"], "beta": stock["beta"],
                "jumpFrequency": round(p.lam, 2), "meanJumpSizePct": round(p.m_j * 100, 2),
                "riskScore": score, "riskLevel": level,
                "returnDistribution": dist,
                "provenance": {
                    "method": "Historical simulation on overlapping holding-period returns",
                    "holdingPeriodDays": horizon, "lookbackObservations": int(len(daily)),
                    "monteCarloMerton95VarPct": round(mc95.var_percentage * 100, 3),
                    "monteCarloMerton95EsPct": round(mc95.es_percentage * 100, 3),
                    "riskScoreRule": "min(100, 2 x annualised volatility %); LOW<15, MODERATE<25, HIGH<40, else EXTREME",
                    "sharpeNote": "Return / volatility with 0% risk-free rate",
                    "amountUnit": "currency per share",
                },
                "disclaimer": DISCLAIMER,
            })
        except ValueError as exc:
            return _error(exc, status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            return _error(exc)


class IpoV1View(APIView):
    def post(self, request):
        d = request.data
        try:
            cutoff = float(d["priceBandMax"])
            retail = float(d.get("retailSubscriptionMultiple", 1.0))
            qib = float(d.get("qibSubscriptionMultiple", 1.0))
            nii = float(d.get("niiSubscriptionMultiple", 1.0))
            gmp_rs = float(d.get("greyMarketPremium") or 0.0)
            pe = float(d.get("peRatio") or 0.0)
            spe = float(d.get("sectorPe") or 0.0)
            qq, nq, rq = (float(d.get(k, v)) for k, v in
                          (("qibQuotaPct", 50), ("niiQuotaPct", 15), ("retailQuotaPct", 35)))
            total = (qib * qq + nii * nq + retail * rq) / max(qq + nq + rq, 1e-9)
            ipo = IPOMarketData(
                company_name=d.get("companyName", "IPO"), symbol="IPO",
                issue_price_min=float(d["priceBandMin"]), issue_price_max=cutoff,
                issue_price_final=cutoff, lot_size=int(d["lotSize"]),
                issue_size_crores=float(d["issueSizeCr"]),
                qib_subscription=qib, nii_subscription=nii, rii_subscription=retail,
                total_subscription=total, grey_market_premium_pct=gmp_rs / cutoff * 100,
                pe_ratio=pe, industry_pe=spe,
            )
            res = analyze_ipo(ipo)
            prob = min(1.0, 1.0 / retail) if retail > 1 else 1.0
            lot_cost = cutoff * ipo.lot_size
            exp_gain = res.expected_listing_gain_pct
            scen = [
                ("Bear case (5th pct)", res.bear_listing_price, 0.25, "Weak listing; model downside tail."),
                ("Base case (mean)", res.expected_listing_price, 0.50, "Central scenario under stated assumptions."),
                ("Bull case (95th pct)", res.bull_listing_price, 0.25, "Strong listing; model upside tail."),
            ]
            return Response({
                "companyName": res.company_name, "sector": d.get("sector", "—"),
                "cutOffPrice": cutoff, "minimumInvestmentPerLot": round(lot_cost, 2),
                "valuationAnalysis": {"valuationStatus": res.valuation_status.replace("_", " ").title(),
                                      "peRatio": pe, "sectorPe": spe},
                "allotmentOdds": {
                    "retailSubscriptionMultiple": retail, "qibSubscriptionMultiple": qib,
                    "niiSubscriptionMultiple": nii,
                    "retailLotteryProbabilityPct": round(prob * 100, 1),
                    "oddsRatio": f"~1 in {max(1, round(1 / prob))}",
                    "description": "Approximation: 1 / retail subscription multiple (SEBI lot-wise lottery).",
                    "sebiRuleNote": "Retail allotment is by lottery of minimum bid lots when oversubscribed.",
                },
                "scenarios": [{
                    "name": n, "projectedListingPrice": round(px, 2),
                    "projectedGainPct": round((px / cutoff - 1) * 100, 2),
                    "probabilityWeight": w, "description": desc,
                } for n, px, w, desc in scen],
                "expectedListingGainPct": round(exp_gain, 2),
                "day1VaR95Amount": round(cutoff - res.bear_listing_price, 2),
                "day1VaR95Pct": round((1 - res.bear_listing_price / cutoff) * 100, 2),
                "userEnteredAssumptions": dict(d),
                "modelAssumptions": {"assumptions": res.assumptions_log, "limitations": res.limitations,
                                     "note": "Heuristic prior (not fitted to data): see quant_engine/ipo_analysis.py"},
                "disclaimer": DISCLAIMER,
            })
        except (KeyError, ValueError) as exc:
            return _error(f"Invalid IPO input: {exc}", status.HTTP_400_BAD_REQUEST)
