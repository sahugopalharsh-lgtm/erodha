"""
Erodha API Views
================
Django REST Framework view handlers for stochastic forecasting and risk assessment.
"""

import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import numpy as np
import pandas as pd

from api.serializers import (
    MarketDataRequestSerializer,
    ForecastRequestSerializer,
    RiskRequestSerializer,
    BacktestRequestSerializer,
    IPOAnalysisRequestSerializer,
)
from api.market_data_service import fetch_historical_prices
from quant_engine.estimation import estimate_model_parameters, estimate_merton_mle
from quant_engine.monte_carlo import run_monte_carlo_forecast
from quant_engine.risk import (
    generate_risk_report, compute_parametric_var_es,
    compute_empirical_var_es, horizon_returns_from_daily,
)
from quant_engine.validation import evaluate_forecast_models
from quant_engine.ipo_analysis import IPOMarketData, analyze_ipo

_STARTED_AT = time.time()


class HealthCheckView(APIView):
    """Health check endpoint to verify backend operational readiness."""
    def get(self, request):
        return Response({
            "status": "healthy",
            "service": "Erodha Quantitative Backend",
            "version": "0.1.0",
            "quant_engine": "operational",
            "environment": "development",
            "activeDataProvider": "yfinance",
            "demoFallbackEnabled": True,
            "uptimeSeconds": int(time.time() - _STARTED_AT),
        }, status=status.HTTP_200_OK)


class MarketDataView(APIView):
    """Retrieves validated historical prices and return statistics."""
    def get(self, request):
        serializer = MarketDataRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        symbol = serializer.validated_data["symbol"]
        period = serializer.validated_data["period"]

        try:
            prices_s, ret_series, val_res, is_synth = fetch_historical_prices(symbol, period)
            stats = ret_series.stats

            # Subsample prices if too large for clean JSON payload
            date_strings = [d.strftime("%Y-%m-%d") for d in prices_s.index]
            price_values = [round(float(p), 4) for p in prices_s.values]

            # Estimated model parameters
            params = estimate_merton_mle(ret_series, symbol=symbol)

            return Response({
                "symbol": symbol,
                "is_synthetic": is_synth,
                "is_adjusted": val_res.is_adjusted,
                "observation_count": val_res.observation_count,
                "start_date": val_res.start_date.strftime("%Y-%m-%d"),
                "end_date": val_res.end_date.strftime("%Y-%m-%d"),
                "warnings": list(val_res.warnings),
                "latest_price": round(float(prices_s.iloc[-1]), 4),
                "dates": date_strings,
                "prices": price_values,
                "statistics": {
                    "annualized_log_return": round(stats.annualized_log_return, 4),
                    "annualized_volatility": round(stats.annualized_volatility, 4),
                    "arithmetic_drift_mu": round(stats.drift_mu, 4),
                    "skewness": round(stats.skewness, 4),
                    "excess_kurtosis": round(stats.excess_kurtosis, 4),
                    "jarque_bera_stat": round(stats.jarque_bera_stat, 2),
                    "jarque_bera_p_value": round(stats.jarque_bera_p_value, 6),
                    "is_normal": stats.is_normal_5pct,
                },
                "calibrated_parameters": {
                    "gbm_mu": round(params.mu_gbm, 4),
                    "gbm_sigma": round(params.sigma_gbm, 4),
                    "merton_continuous_sigma": round(params.sigma_continuous, 4),
                    "merton_lambda": round(params.lam, 4),
                    "merton_m_j": round(params.m_j, 4),
                    "merton_delta_j": round(params.delta_j, 4),
                    "merton_kappa": round(params.kappa, 4),
                    "jump_count": params.jump_count,
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ForecastGBMView(APIView):
    """Executes Geometric Brownian Motion Monte Carlo simulation."""
    def post(self, request):
        serializer = ForecastRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        symbol = data["symbol"]
        horizon_days = data["horizon_days"]
        n_paths = data["n_paths"]
        seed = data.get("seed", 42)

        prices_s, ret_series, _, _ = fetch_historical_prices(symbol)
        s0 = data["s0"] if data.get("s0") is not None else float(prices_s.iloc[-1])
        mu = data["mu"] if data.get("mu") is not None else ret_series.stats.drift_mu
        sigma = data["sigma"] if data.get("sigma") is not None else ret_series.stats.annualized_volatility

        forecast = run_monte_carlo_forecast(
            model="GBM",
            s0=s0,
            mu=mu,
            sigma=sigma,
            horizon_days=horizon_days,
            n_paths=n_paths,
            seed=seed,
        )

        return Response({
            "model": "GBM",
            "symbol": symbol,
            "s0": round(s0, 2),
            "mu": round(mu, 4),
            "sigma": round(sigma, 4),
            "horizon_days": horizon_days,
            "n_paths": n_paths,
            "time_steps": [round(float(t), 4) for t in forecast.time_grid],
            "quantiles": {
                "q05": [round(float(p), 2) for p in forecast.q05_path],
                "q25": [round(float(p), 2) for p in forecast.q25_path],
                "median": [round(float(p), 2) for p in forecast.median_path],
                "q75": [round(float(p), 2) for p in forecast.q75_path],
                "q95": [round(float(p), 2) for p in forecast.q95_path],
                "mean": [round(float(p), 2) for p in forecast.mean_path],
            },
            "sample_paths": [[round(float(p), 2) for p in path] for path in forecast.sample_paths.T[:15]],
            "terminal": {
                "mean": round(forecast.terminal_mean, 2),
                "median": round(forecast.terminal_median, 2),
                "std": round(forecast.terminal_std, 2),
                "q05": round(forecast.terminal_q05, 2),
                "q95": round(forecast.terminal_q95, 2),
                "mc_standard_error": round(forecast.mc_standard_error, 4),
                "mc_mean_ci_95": [round(forecast.mc_mean_ci_95[0], 2), round(forecast.mc_mean_ci_95[1], 2)],
            }
        }, status=status.HTTP_200_OK)


class ForecastMertonView(APIView):
    """Executes Merton Jump-Diffusion Monte Carlo simulation."""
    def post(self, request):
        serializer = ForecastRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        symbol = data["symbol"]
        horizon_days = data["horizon_days"]
        n_paths = data["n_paths"]
        seed = data.get("seed", 42)

        prices_s, ret_series, _, _ = fetch_historical_prices(symbol)
        if data.get("calibration", "mle") == "mle":
            params = estimate_merton_mle(ret_series, symbol=symbol)
        else:
            params = estimate_model_parameters(ret_series, symbol=symbol)

        s0 = data["s0"] if data.get("s0") is not None else float(prices_s.iloc[-1])
        mu = data["mu"] if data.get("mu") is not None else params.mu_merton
        sigma = data["sigma"] if data.get("sigma") is not None else params.sigma_continuous
        lam = data.get("lam") if data.get("lam") is not None else params.lam
        m_j = data.get("m_j") if data.get("m_j") is not None else params.m_j
        delta_j = data.get("delta_j") if data.get("delta_j") is not None else params.delta_j

        forecast = run_monte_carlo_forecast(
            model="MERTON",
            s0=s0,
            mu=mu,
            sigma=sigma,
            lam=lam,
            m_j=m_j,
            delta_j=delta_j,
            horizon_days=horizon_days,
            n_paths=n_paths,
            seed=seed,
        )

        return Response({
            "model": "MERTON",
            "symbol": symbol,
            "s0": round(s0, 2),
            "mu": round(mu, 4),
            "sigma": round(sigma, 4),
            "lambda": round(lam, 4),
            "m_j": round(m_j, 4),
            "delta_j": round(delta_j, 4),
            "horizon_days": horizon_days,
            "n_paths": n_paths,
            "time_steps": [round(float(t), 4) for t in forecast.time_grid],
            "quantiles": {
                "q05": [round(float(p), 2) for p in forecast.q05_path],
                "q25": [round(float(p), 2) for p in forecast.q25_path],
                "median": [round(float(p), 2) for p in forecast.median_path],
                "q75": [round(float(p), 2) for p in forecast.q75_path],
                "q95": [round(float(p), 2) for p in forecast.q95_path],
                "mean": [round(float(p), 2) for p in forecast.mean_path],
            },
            "sample_paths": [[round(float(p), 2) for p in path] for path in forecast.sample_paths.T[:15]],
            "terminal": {
                "mean": round(forecast.terminal_mean, 2),
                "median": round(forecast.terminal_median, 2),
                "std": round(forecast.terminal_std, 2),
                "q05": round(forecast.terminal_q05, 2),
                "q95": round(forecast.terminal_q95, 2),
                "mc_standard_error": round(forecast.mc_standard_error, 4),
                "mc_mean_ci_95": [round(forecast.mc_mean_ci_95[0], 2), round(forecast.mc_mean_ci_95[1], 2)],
            }
        }, status=status.HTTP_200_OK)


class RiskAnalysisView(APIView):
    """Computes empirical and parametric VaR, Expected Shortfall, and Drawdown."""
    def post(self, request):
        serializer = RiskRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        symbol = serializer.validated_data["symbol"]
        portfolio_val = serializer.validated_data["portfolio_value"]
        conf_level = serializer.validated_data["confidence_level"]
        horizon = serializer.validated_data["horizon_days"]

        period = serializer.validated_data["period"]
        n_paths = serializer.validated_data["n_paths"]
        seed = serializer.validated_data.get("seed", 42)

        prices_s, ret_series, _, _ = fetch_historical_prices(symbol, period=period)
        daily = ret_series.simple_returns.values
        try:
            returns = horizon_returns_from_daily(daily, horizon)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        report = generate_risk_report(
            returns=returns,
            prices=prices_s.values,
            portfolio_value=portfolio_val,
            horizon_days=horizon,
            method="HISTORICAL",
        )

        # Parametric (Gaussian) risk, daily moments scaled to the horizon
        mean_ret = float(np.mean(daily)) * horizon
        vol_ret = float(np.std(daily, ddof=1)) * np.sqrt(horizon)
        param_risk_95 = compute_parametric_var_es(mean_ret, vol_ret, 0.95, portfolio_val, horizon)
        param_risk_99 = compute_parametric_var_es(mean_ret, vol_ret, 0.99, portfolio_val, horizon)

        # Model-based Monte Carlo risk: GBM vs Merton jump-diffusion over the horizon
        s0 = float(prices_s.iloc[-1])
        gbm_p = estimate_model_parameters(ret_series, symbol=symbol)
        mer_p = estimate_merton_mle(ret_series, symbol=symbol)
        fc_gbm = run_monte_carlo_forecast(
            model="GBM", s0=s0, mu=gbm_p.mu_gbm, sigma=gbm_p.sigma_gbm,
            horizon_days=horizon, n_steps=horizon, n_paths=n_paths, seed=seed)
        fc_mer = run_monte_carlo_forecast(
            model="MERTON", s0=s0, mu=mer_p.mu_merton, sigma=mer_p.sigma_continuous,
            lam=mer_p.lam, m_j=mer_p.m_j, delta_j=mer_p.delta_j,
            horizon_days=horizon, n_steps=horizon, n_paths=n_paths, seed=seed)

        def _mc_block(fc):
            r_mc = fc.terminal_prices / s0 - 1.0
            out = {}
            for lvl in (0.95, 0.99):
                m = compute_empirical_var_es(r_mc, lvl, portfolio_val, horizon, "MONTE_CARLO")
                tag = int(lvl * 100)
                out[f"var_{tag}_pct"] = round(m.var_percentage * 100.0, 3)
                out[f"var_{tag}_amount"] = round(m.var_amount, 2)
                out[f"es_{tag}_pct"] = round(m.es_percentage * 100.0, 3)
                out[f"es_{tag}_amount"] = round(m.es_amount, 2)
            return out

        # Downsample loss distribution for client chart
        losses_sample = [round(float(l), 5) for l in report.loss_distribution[:500]]

        return Response({
            "symbol": symbol,
            "portfolio_value": portfolio_val,
            "horizon_days": horizon,
            "max_drawdown_pct": round(report.max_drawdown_percentage * 100.0, 2),
            "historical_risk": {
                "var_95_pct": round(report.var_95.var_percentage * 100.0, 3),
                "var_95_amount": round(report.var_95.var_amount, 2),
                "es_95_pct": round(report.var_95.es_percentage * 100.0, 3),
                "es_95_amount": round(report.var_95.es_amount, 2),
                "var_99_pct": round(report.var_99.var_percentage * 100.0, 3),
                "var_99_amount": round(report.var_99.var_amount, 2),
                "es_99_pct": round(report.var_99.es_percentage * 100.0, 3),
                "es_99_amount": round(report.var_99.es_amount, 2),
            },
            "monte_carlo_gbm_risk": _mc_block(fc_gbm),
            "monte_carlo_merton_risk": _mc_block(fc_mer),
            "merton_parameters": {
                "sigma": round(mer_p.sigma_continuous, 4), "lambda": round(mer_p.lam, 3),
                "m_j": round(mer_p.m_j, 4), "delta_j": round(mer_p.delta_j, 4),
            },
            "parametric_risk": {
                "var_95_pct": round(param_risk_95.var_percentage * 100.0, 3),
                "var_95_amount": round(param_risk_95.var_amount, 2),
                "es_95_pct": round(param_risk_95.es_percentage * 100.0, 3),
                "es_95_amount": round(param_risk_95.es_amount, 2),
                "var_99_pct": round(param_risk_99.var_percentage * 100.0, 3),
                "var_99_amount": round(param_risk_99.var_amount, 2),
                "es_99_pct": round(param_risk_99.es_percentage * 100.0, 3),
                "es_99_amount": round(param_risk_99.es_amount, 2),
            },
            "loss_distribution_sample": losses_sample,
        }, status=status.HTTP_200_OK)


class BacktestView(APIView):
    """Executes chronological out-of-sample backtesting and Kupiec POF testing."""
    def post(self, request):
        serializer = BacktestRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        symbol = serializer.validated_data["symbol"]
        split_ratio = serializer.validated_data["split_ratio"]
        n_paths = serializer.validated_data["n_paths"]
        seed = serializer.validated_data.get("seed", 42)

        prices_s, _, _, _ = fetch_historical_prices(symbol, period="2y")
        res = evaluate_forecast_models(
            price_series=prices_s,
            symbol=symbol,
            split_ratio=split_ratio,
            n_paths=n_paths,
            seed=seed,
        )

        return Response({
            "symbol": symbol,
            "train_observations": res.train_size,
            "test_observations": res.test_size,
            "gbm": {
                "mae": round(res.mae_gbm, 2),
                "rmse": round(res.rmse_gbm, 2),
                "coverage_90_pct": round(res.coverage_90_gbm * 100.0, 1),
            },
            "merton": {
                "mae": round(res.mae_merton, 2),
                "rmse": round(res.rmse_merton, 2),
                "coverage_90_pct": round(res.coverage_90_merton * 100.0, 1),
            },
            "kupiec_pof_test": {
                "failures": res.kupiec_var_95.failures,
                "total_observations": res.kupiec_var_95.total_observations,
                "failure_rate_pct": round(res.kupiec_var_95.failure_rate * 100.0, 2),
                "expected_failure_rate_pct": round(res.kupiec_var_95.expected_failure_rate * 100.0, 2),
                "lr_stat": round(res.kupiec_var_95.likelihood_ratio_stat, 3),
                "p_value": round(res.kupiec_var_95.p_value, 4),
                "is_model_accurate_5pct": res.kupiec_var_95.is_accepted_5pct,
            },
            "best_point_prediction_model": res.best_point_model,
            "best_distribution_model": res.best_distribution_model,
        }, status=status.HTTP_200_OK)


class IPOAnalysisView(APIView):
    """Analyzes IPO subscription signals, valuation, and post-listing scenarios."""
    def post(self, request):
        serializer = IPOAnalysisRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        d = serializer.validated_data
        ipo_data = IPOMarketData(
            company_name=d["company_name"],
            symbol=d["symbol"],
            issue_price_min=d["issue_price_min"],
            issue_price_max=d["issue_price_max"],
            issue_price_final=d["issue_price_final"],
            lot_size=d["lot_size"],
            issue_size_crores=d["issue_size_crores"],
            qib_subscription=d["qib_subscription"],
            nii_subscription=d["nii_subscription"],
            rii_subscription=d["rii_subscription"],
            total_subscription=d["total_subscription"],
            grey_market_premium_pct=d["grey_market_premium_pct"],
            pe_ratio=d["pe_ratio"],
            industry_pe=d["industry_pe"],
        )

        res = analyze_ipo(ipo_data)

        return Response({
            "company_name": res.company_name,
            "issue_price": res.issue_price,
            "expected_listing_price": round(res.expected_listing_price, 2),
            "expected_listing_gain_pct": round(res.expected_listing_gain_pct, 2),
            "bear_listing_price_q05": round(res.bear_listing_price, 2),
            "bull_listing_price_q95": round(res.bull_listing_price, 2),
            "valuation_status": res.valuation_status,
            "assumptions": res.assumptions_log,
            "limitations": res.limitations,
        }, status=status.HTTP_200_OK)
