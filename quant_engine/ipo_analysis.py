"""
Erodha Quantitative Engine: IPO Analysis & Risk Engine
======================================================
Analysis of Initial Public Offerings with explicitly stated assumptions.

Methodology & Principles:
- IPOs lack historical secondary market trading data. Standard continuous
  diffusion (GBM / Merton) cannot be naively calibrated without prior trading days.
- Inputs must be categorized strictly into:
  1. Observed Facts (Issue Price, Issue Size, Shares Offered, Subscription multiples).
  2. Valuation Multiples (P/E Ratio, Implied Market Capitalization).
  3. Model Assumptions (Expected Day-1 Listing Premium distribution, Lock-in Expiry Impact).
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import numpy as np


@dataclass(frozen=True)
class IPOMarketData:
    """Verifiable inputs for an IPO filing."""
    company_name: str
    symbol: str
    issue_price_min: float
    issue_price_max: float
    issue_price_final: float
    lot_size: int
    issue_size_crores: float
    qib_subscription: float       # Qualified Institutional Buyers multiple
    nii_subscription: float       # Non-Institutional Investors multiple
    rii_subscription: float       # Retail Individual Investors multiple
    total_subscription: float     # Weighted aggregate oversubscription
    grey_market_premium_pct: float# GMP as % of issue price (observed grey market signal)
    pe_ratio: float
    industry_pe: float


@dataclass(frozen=True)
class IPOScenarioResult:
    """Simulated post-listing scenario outcomes under stated assumptions."""
    company_name: str
    issue_price: float
    expected_listing_price: float
    expected_listing_gain_pct: float
    bear_listing_price: float     # 5th percentile scenario
    bull_listing_price: float     # 95th percentile scenario
    valuation_status: str         # 'PREMIUM_TO_PEERS', 'DISCOUNT_TO_PEERS', or 'FAIR'
    assumptions_log: List[str]
    limitations: List[str]


def analyze_ipo(
    ipo_data: IPOMarketData,
    market_sentiment_factor: float = 1.0,
    n_scenarios: int = 5000,
    seed: int = 42,
) -> IPOScenarioResult:
    """
    Evaluates an IPO by synthesizing subscription demand, GMP signals,
    and peer valuation indicators under explicitly documented assumptions.
    """
    assumptions: List[str] = []
    limitations: List[str] = [
        "IPO stocks have zero historical secondary market trading data; parameters are based on synthetic priors.",
        "Grey Market Premium (GMP) is an unregulated indicator and subject to severe illiquidity distortions.",
        "Anchor and institutional lock-in expiries (30-day / 90-day) often induce discontinuous downward supply shocks.",
    ]

    issue_p = ipo_data.issue_price_final

    # 1. Valuation benchmark against peers
    if ipo_data.industry_pe > 0 and ipo_data.pe_ratio > 0:
        pe_diff_pct = (ipo_data.pe_ratio - ipo_data.industry_pe) / ipo_data.industry_pe
        if pe_diff_pct > 0.15:
            valuation_status = "PREMIUM_TO_PEERS"
            assumptions.append(f"P/E ratio of {ipo_data.pe_ratio:.1f} is at a >15% premium to industry mean ({ipo_data.industry_pe:.1f}).")
        elif pe_diff_pct < -0.15:
            valuation_status = "DISCOUNT_TO_PEERS"
            assumptions.append(f"P/E ratio of {ipo_data.pe_ratio:.1f} is at a >15% discount to industry mean ({ipo_data.industry_pe:.1f}).")
        else:
            valuation_status = "FAIR_VALUATION"
            assumptions.append("Valuation is in line with industry peers (+/- 15%).")
    else:
        valuation_status = "NOT_AVAILABLE"
        assumptions.append("Industry or IPO P/E unavailable.")

    # 2. Demand-based listing gain simulation
    # Empirical literature indicates listing gain correlates with QIB oversubscription and GMP
    # Model: Listing_Gain_% ~ Normal( mu_gain, sigma_gain^2 )
    # mu_gain is anchored on GMP and weighted institutional demand
    gmp_signal = ipo_data.grey_market_premium_pct / 100.0
    demand_signal = np.log1p(max(0.0, ipo_data.qib_subscription)) * 0.04
    
    base_mu = (0.6 * gmp_signal + 0.4 * demand_signal) * market_sentiment_factor
    base_sigma = max(0.08, 0.15 / (1.0 + np.log1p(ipo_data.total_subscription)))

    assumptions.append(
        f"Listing gain distribution modeled as Normal(mean={base_mu*100:.1f}%, std={base_sigma*100:.1f}%) "
        f"weighted by GMP ({ipo_data.grey_market_premium_pct:.1f}%) and institutional subscription ({ipo_data.qib_subscription:.1f}x)."
    )

    rng = np.random.default_rng(seed)
    sim_returns = rng.normal(base_mu, base_sigma, size=n_scenarios)
    sim_prices = issue_p * (1.0 + sim_returns)

    expected_p = float(np.mean(sim_prices))
    expected_gain_pct = float(np.mean(sim_returns) * 100.0)
    bear_p = float(np.percentile(sim_prices, 5))
    bull_p = float(np.percentile(sim_prices, 95))

    return IPOScenarioResult(
        company_name=ipo_data.company_name,
        issue_price=issue_p,
        expected_listing_price=expected_p,
        expected_listing_gain_pct=expected_gain_pct,
        bear_listing_price=bear_p,
        bull_listing_price=bull_p,
        valuation_status=valuation_status,
        assumptions_log=assumptions,
        limitations=limitations,
    )
