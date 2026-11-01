"""
Erodha: Quantitative Stock Forecasting & Jump-Diffusion Risk Tool
=================================================================
Interactive Streamlit Dashboard.
Powered by Django REST Framework backend & Pure NumPy/SciPy Quant Engine.
"""

import sys
from pathlib import Path
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# Add frontend directory to path
FRONTEND_DIR = Path(__file__).resolve().parent
if str(FRONTEND_DIR) not in sys.path:
    sys.path.insert(0, str(FRONTEND_DIR))

from api_client import ErodhaAPIClient

# Page configuration
st.set_page_config(
    page_title="Erodha | Stochastic Equity Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom styling
st.markdown("""
<style>
    .metric-card {
        background-color: #1e222d;
        border-radius: 8px;
        padding: 14px;
        border: 1px solid #2a2e39;
        margin-bottom: 10px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: #4da3ff;
    }
    .metric-label {
        font-size: 13px;
        color: #8b949e;
        margin-bottom: 4px;
    }
    .warning-box {
        background-color: #3b2a1a;
        border-left: 4px solid #f0883e;
        padding: 12px;
        border-radius: 4px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize API Client
client = ErodhaAPIClient()

# Sidebar: Controls & Ticker Selection
st.sidebar.title("📈 ERODHA")
st.sidebar.caption("Jump-Diffusion & Stochastic Risk Engine")

# Check Backend Status
health = client.check_health()
if health["status"] == "connected":
    st.sidebar.success("🟢 Django Backend: Connected")
else:
    st.sidebar.error("🔴 Backend Disconnected (Start manage.py runserver)")

st.sidebar.markdown("---")
st.sidebar.subheader("Asset & Market Settings")

symbol_presets = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "RELIANCE.NS", "TCS.NS", "Custom"]
selected_symbol = st.sidebar.selectbox("Select Symbol", symbol_presets, index=0)

if selected_symbol == "Custom":
    ticker = st.sidebar.text_input("Enter Ticker", value="SPY").strip().upper()
else:
    ticker = selected_symbol

period = st.sidebar.selectbox("Historical Window", ["3mo", "6mo", "1y", "2y", "5y"], index=2)
portfolio_val = st.sidebar.number_input("Portfolio Position Value ($)", min_value=1000.0, value=100_000.0, step=5000.0)

# Fetch Market Data
@st.cache_data(ttl=60)
def load_data(sym: str, per: str):
    return client.get_market_data(sym, per)

data_error = None
market_data = None
try:
    with st.spinner(f"Retrieving and validating historical series for {ticker}..."):
        market_data = load_data(ticker, period)
except Exception as e:
    data_error = str(e)

# Header Title
st.title("ERODHA: Quantitative Forecasting & Risk Engine")
st.caption("Stochastic Decision-Support & Mathematical Tail-Risk Platform")

if data_error:
    st.error(f"Failed to fetch market data: {data_error}")
    st.stop()

# Main Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Market Overview & Data",
    "🔮 Stochastic Forecasting",
    "🛡️ Tail Risk & VaR",
    "🧪 Model Backtesting",
    "🚀 IPO Valuation Engine",
])

# -------------------------------------------------------------
# TAB 1: Market Overview & Data Validation
# -------------------------------------------------------------
with tab1:
    st.subheader(f"Historical Price Series: {ticker}")

    if market_data.get("is_synthetic"):
        st.warning("⚠️ **Notice**: Yahoo Finance was throttled or unreachable; using verified synthetic Brownian price series with realistic parameters.")

    if market_data.get("warnings"):
        with st.expander("Data Quality & Integrity Notes", expanded=False):
            for w in market_data["warnings"]:
                st.info(f"ℹ️ {w}")

    # Top KPI Metrics
    stats = market_data["statistics"]
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Latest Price", f"${market_data['latest_price']:,.2f}")
    c2.metric("Annualized Volatility", f"{stats['annualized_volatility']*100:.2f}%")
    c3.metric("Annualized Drift (μ)", f"{stats['arithmetic_drift_mu']*100:.2f}%")
    c4.metric("Excess Kurtosis", f"{stats['excess_kurtosis']:.2f}")
    c5.metric("Normality (JB p-val)", f"{stats['jarque_bera_p_value']:.4f}",
              delta="Gaussian" if stats["is_normal"] else "Fat-Tailed / Jumps",
              delta_color="normal" if stats["is_normal"] else "inverse")

    # Interactive Price & Log Return Charts
    dates = pd.to_datetime(market_data["dates"])
    prices = market_data["prices"]
    df_chart = pd.DataFrame({"Date": dates, "Price": prices})

    fig_price = px.line(
        df_chart, x="Date", y="Price",
        title=f"{ticker} Adjusted Historical Prices ({market_data['start_date']} to {market_data['end_date']})",
        labels={"Price": "Price ($)", "Date": "Date"}
    )
    fig_price.update_layout(template="plotly_dark", height=400, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_price, use_container_width=True)

    # Calibrated Jump Parameters Overview
    st.subheader("Calibrated Jump-Diffusion vs. GBM Parameters")
    params = market_data["calibrated_parameters"]
    p1, p2, p3, p4 = st.columns(4)
    p1.metric("GBM Total Volatility (σ)", f"{params['gbm_sigma']*100:.2f}%")
    p2.metric("Continuous Volatility (σ_cont)", f"{params['merton_continuous_sigma']*100:.2f}%")
    p3.metric("Jump Intensity (λ / yr)", f"{params['merton_lambda']:.2f} jumps")
    p4.metric("Mean Jump Size (m_J)", f"{params['merton_m_j']*100:.2f}%")


# -------------------------------------------------------------
# TAB 2: Stochastic Forecasting (GBM vs. Merton)
# -------------------------------------------------------------
with tab2:
    st.subheader("Stochastic Multi-Path Monte Carlo Forecasting")
    st.markdown("""
    Compare standard **Geometric Brownian Motion (GBM)** with the **Merton Jump-Diffusion Model**.
    Predictive quantile envelopes represent model scenario distributions, **not** guaranteed price bounds.
    """)

    col_ctrl1, col_ctrl2, col_ctrl3, col_ctrl4 = st.columns(4)
    model_choice = col_ctrl1.selectbox("Stochastic Model", ["Merton Jump-Diffusion", "Geometric Brownian Motion (GBM)"])
    horizon_days = col_ctrl2.slider("Forecast Horizon (Trading Days)", min_value=10, max_value=504, value=252, step=10)
    n_paths = col_ctrl3.select_slider("Simulation Paths (M)", options=[1000, 2500, 5000, 10000], value=5000)
    seed = col_ctrl4.number_input("Random Seed", value=42, step=1)

    with st.spinner("Executing vectorized Monte Carlo simulation..."):
        if model_choice.startswith("Geometric"):
            fc = client.get_gbm_forecast(
                symbol=ticker,
                horizon_days=horizon_days,
                n_paths=n_paths,
                seed=seed,
                s0=market_data["latest_price"],
            )
        else:
            fc = client.get_merton_forecast(
                symbol=ticker,
                horizon_days=horizon_days,
                n_paths=n_paths,
                seed=seed,
                s0=market_data["latest_price"],
            )

    # Plotting Quantile Cones and Sample Paths
    steps = np.arange(len(fc["time_steps"]))
    q = fc["quantiles"]

    fig_fan = go.Figure()

    # 5% - 95% Quantile Envelope (Outer Cone)
    fig_fan.add_trace(go.Scatter(
        x=np.concatenate([steps, steps[::-1]]),
        y=np.concatenate([q["q95"], q["q05"][::-1]]),
        fill='toself',
        fillcolor='rgba(77, 163, 255, 0.15)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip",
        showlegend=True,
        name='90% Predictive Envelope (5th - 95th %ile)'
    ))

    # 25% - 75% Quantile Envelope (Inner Cone)
    fig_fan.add_trace(go.Scatter(
        x=np.concatenate([steps, steps[::-1]]),
        y=np.concatenate([q["q75"], q["q25"][::-1]]),
        fill='toself',
        fillcolor='rgba(77, 163, 255, 0.30)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip",
        showlegend=True,
        name='50% Interquartile Envelope (25th - 75th %ile)'
    ))

    # Sample paths
    for i, path in enumerate(fc["sample_paths"][:8]):
        fig_fan.add_trace(go.Scatter(
            x=steps, y=path,
            mode='lines',
            line=dict(width=0.8, color='rgba(200, 200, 200, 0.3)'),
            showlegend=True if i == 0 else False,
            name='Sample Monte Carlo Trajectories',
            hoverinfo="skip"
        ))

    # Median Path
    fig_fan.add_trace(go.Scatter(
        x=steps, y=q["median"],
        mode='lines',
        line=dict(color='#00f0ff', width=2.5),
        name='Median Scenario (50th %ile)'
    ))

    # Theoretical Mean Path
    fig_fan.add_trace(go.Scatter(
        x=steps, y=q["mean"],
        mode='lines',
        line=dict(color='#ffaa00', width=2, dash='dot'),
        name='Expected Value E[S_t]'
    ))

    fig_fan.update_layout(
        title=f"{ticker} — {model_choice} ({n_paths:,} Paths, {horizon_days} Trading Days)",
        xaxis_title="Future Trading Days (Δt = 1/252 yr)",
        yaxis_title="Projected Asset Price ($)",
        template="plotly_dark",
        height=520,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_fan, use_container_width=True)

    # Terminal Scenario Summary
    term = fc["terminal"]
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Expected Terminal Price", f"${term['mean']:.2f}")
    m2.metric("Median Terminal Price", f"${term['median']:.2f}")
    m3.metric("5th %ile (Bearish Floor)", f"${term['q05']:.2f}")
    m4.metric("95th %ile (Bullish Ceiling)", f"${term['q95']:.2f}")

    st.caption(
        f"**Monte Carlo Precision**: Terminal Mean = ${term['mean']:.2f} "
        f"(95% MC CI: [${term['mc_mean_ci_95'][0]:.2f}, ${term['mc_mean_ci_95'][1]:.2f}], "
        f"SE = ${term['mc_standard_error']:.3f})"
    )


# -------------------------------------------------------------
# TAB 3: Tail Risk & Value at Risk (VaR)
# -------------------------------------------------------------
with tab3:
    st.subheader("Financial Tail Risk & Extreme Loss Assessment")
    st.markdown("""
    **Value at Risk (VaR)** measures the minimum loss expected with confidence $\\alpha$.
    **Expected Shortfall (ES / CVaR)** measures the average loss when VaR is breached.
    Losses are defined as positive values ($L = -\\Delta V$).
    """)

    risk_horizon = st.select_slider("Holding period (trading days)", options=[1, 5, 10, 21], value=1)
    with st.spinner("Calculating historical, Gaussian and Monte Carlo (GBM vs Merton) tail risk..."):
        risk_data = client.get_risk_metrics(
            symbol=ticker,
            portfolio_value=portfolio_val,
            confidence_level=0.95,
            horizon_days=risk_horizon
        )

    hist_r = risk_data["historical_risk"]
    param_r = risk_data["parametric_risk"]

    rk1, rk2, rk3, rk4 = st.columns(4)
    rk1.metric(f"{risk_horizon}-Day 95% VaR (Historical)", f"${hist_r['var_95_amount']:,.2f}", f"{hist_r['var_95_pct']:.2f}%")
    rk2.metric(f"{risk_horizon}-Day 95% Expected Shortfall", f"${hist_r['es_95_amount']:,.2f}", f"{hist_r['es_95_pct']:.2f}%")
    rk3.metric(f"{risk_horizon}-Day 99% VaR (Historical)", f"${hist_r['var_99_amount']:,.2f}", f"{hist_r['var_99_pct']:.2f}%")
    rk4.metric("Maximum Historical Drawdown", f"{risk_data['max_drawdown_pct']:.2f}%")

    # Risk Comparison Table
    df_risk = pd.DataFrame({
        "Metric": ["95% Value at Risk (VaR)", "95% Expected Shortfall (ES)", "99% Value at Risk (VaR)", "99% Expected Shortfall (ES)"],
        "Empirical Historical (%)": [f"{hist_r['var_95_pct']:.2f}%", f"{hist_r['es_95_pct']:.2f}%", f"{hist_r['var_99_pct']:.2f}%", f"{hist_r['es_99_pct']:.2f}%"],
        "Empirical Dollar ($)": [f"${hist_r['var_95_amount']:,.2f}", f"${hist_r['es_95_amount']:,.2f}", f"${hist_r['var_99_amount']:,.2f}", f"${hist_r['es_99_amount']:,.2f}"],
        "Parametric Gaussian (%)": [f"{param_r['var_95_pct']:.2f}%", f"{param_r['es_95_pct']:.2f}%", f"{param_r['var_99_pct']:.2f}%", f"{param_r['es_99_pct']:.2f}%"],
        "Parametric Dollar ($)": [f"${param_r['var_95_amount']:,.2f}", f"${param_r['es_95_amount']:,.2f}", f"${param_r['var_99_amount']:,.2f}", f"${param_r['es_99_amount']:,.2f}"],
    })
    st.table(df_risk)

    # Model-based Monte Carlo risk: does adding jumps change the tail?
    g, m = risk_data["monte_carlo_gbm_risk"], risk_data["monte_carlo_merton_risk"]
    st.markdown("**Model-based Monte Carlo risk (same horizon): GBM vs Merton jump-diffusion**")
    st.table(pd.DataFrame({
        "Metric": ["95% VaR", "95% ES", "99% VaR", "99% ES"],
        "GBM (%)": [f"{g['var_95_pct']:.2f}%", f"{g['es_95_pct']:.2f}%", f"{g['var_99_pct']:.2f}%", f"{g['es_99_pct']:.2f}%"],
        "Merton (%)": [f"{m['var_95_pct']:.2f}%", f"{m['es_95_pct']:.2f}%", f"{m['var_99_pct']:.2f}%", f"{m['es_99_pct']:.2f}%"],
    }))
    mp = risk_data["merton_parameters"]
    st.caption(f"Merton MLE calibration: sigma={mp['sigma']:.3f}, lambda={mp['lambda']:.2f}/yr, "
               f"jump mean={mp['m_j']:.3f}, jump std={mp['delta_j']:.3f}")

    # Loss Distribution Histogram with Cutoffs
    losses = np.array(risk_data["loss_distribution_sample"]) * 100.0  # in percent
    fig_hist = px.histogram(
        losses, nbins=60,
        title=f"Empirical {risk_horizon}-Day Loss Distribution (Positive Values = Loss)",
        labels={"value": "Daily Loss (%)"},
        color_discrete_sequence=['#4da3ff']
    )
    fig_hist.add_vline(x=hist_r["var_95_pct"], line_dash="dash", line_color="#ffcc00", annotation_text="95% VaR")
    fig_hist.add_vline(x=hist_r["es_95_pct"], line_dash="solid", line_color="#ff4444", annotation_text="95% Expected Shortfall")
    fig_hist.update_layout(template="plotly_dark", height=380, showlegend=False)
    st.plotly_chart(fig_hist, use_container_width=True)


# -------------------------------------------------------------
# TAB 4: Model Backtesting & Evaluation
# -------------------------------------------------------------
with tab4:
    st.subheader("Historical Model Backtesting & VaR Validation")
    st.markdown("""
    Models are calibrated **strictly** on the training partition (first 80% of data).
    Predictions are evaluated on the out-of-sample test partition (last 20%) with **zero data leakage**.
    """)

    if st.button("Run Full Chronological Backtest"):
        with st.spinner("Running out-of-sample backtest & Kupiec POF test..."):
            bt = client.get_backtest(symbol=ticker, split_ratio=0.8, n_paths=2000)

        b1, b2, b3 = st.columns(3)
        b1.metric("Training Sample Size", f"{bt['train_observations']} days")
        b2.metric("Out-of-Sample Test Size", f"{bt['test_observations']} days")
        b3.metric("Kupiec VaR Status", "Passed (Accurate)" if bt["kupiec_pof_test"]["is_model_accurate_5pct"] else "Rejected")

        # Comparison Table
        df_bt = pd.DataFrame({
            "Evaluation Metric": ["Mean Absolute Error (MAE)", "Root Mean Squared Error (RMSE)", "90% Envelope Coverage (Nominal: 90%)"],
            "Geometric Brownian Motion (GBM)": [f"${bt['gbm']['mae']:.2f}", f"${bt['gbm']['rmse']:.2f}", f"{bt['gbm']['coverage_90_pct']:.1f}%"],
            "Merton Jump-Diffusion": [f"${bt['merton']['mae']:.2f}", f"${bt['merton']['rmse']:.2f}", f"{bt['merton']['coverage_90_pct']:.1f}%"],
            "Superior Model": [
                bt["best_point_prediction_model"],
                bt["best_point_prediction_model"],
                bt["best_distribution_model"]
            ]
        })
        st.table(df_bt)

        # Kupiec POF Details
        kp = bt["kupiec_pof_test"]
        with st.expander("Kupiec Proportion of Failures (POF) Likelihood Ratio Details", expanded=True):
            st.markdown(f"""
            - **Observed VaR Breaches**: {kp['failures']} out of {kp['total_observations']} days ({kp['failure_rate_pct']:.2f}%)
            - **Expected Failure Rate**: {kp['expected_failure_rate_pct']:.2f}%
            - **Likelihood Ratio Statistic (LR_POF)**: {kp['lr_stat']:.3f}
            - **Chi-Square p-value**: {kp['p_value']:.4f}
            - **Conclusion**: {'Model accurately captures 95% tail risk at 5% significance level.' if kp['is_model_accurate_5pct'] else 'Model tail coverage rejected.'}
            """)


# -------------------------------------------------------------
# TAB 5: IPO Analysis & Risk Scenarios
# -------------------------------------------------------------
with tab5:
    st.subheader("Initial Public Offering (IPO) Valuation & Listing Engine")
    st.markdown("""
    > **Methodology Note**: Standard continuous diffusion models assume established trading history.
    > For unlisted IPOs, listing gain distributions are modeled from verifiable demand fundamentals (QIB subscription, GMP)
    > under explicitly stated assumptions.
    """)

    ipo_col1, ipo_col2 = st.columns(2)
    with ipo_col1:
        ipo_name = st.text_input("Company Name", value="Swiggy Limited IPO")
        ipo_symbol = st.text_input("Proposed Symbol", value="SWIGGY.BO")
        issue_price = st.number_input("Issue Price ($ or ₹)", value=390.0, step=5.0)
        lot_size = st.number_input("Market Lot Size", value=38, step=1)
        issue_size = st.number_input("Issue Size (Cr)", value=11327.0, step=100.0)

    with ipo_col2:
        qib_sub = st.number_input("QIB Subscription (x)", value=6.0, step=0.5)
        nii_sub = st.number_input("NII Subscription (x)", value=1.5, step=0.2)
        rii_sub = st.number_input("Retail Subscription (x)", value=1.2, step=0.1)
        gmp_pct = st.number_input("Grey Market Premium (GMP %)", value=12.0, step=1.0)
        pe_ratio = st.number_input("Company P/E Ratio", value=45.0, step=1.0)
        ind_pe = st.number_input("Industry Benchmark P/E", value=38.0, step=1.0)

    total_sub = (0.5 * qib_sub) + (0.15 * nii_sub) + (0.35 * rii_sub)

    if st.button("Evaluate IPO Listing Scenario"):
        payload = {
            "company_name": ipo_name,
            "symbol": ipo_symbol,
            "issue_price_min": issue_price * 0.95,
            "issue_price_max": issue_price,
            "issue_price_final": issue_price,
            "lot_size": lot_size,
            "issue_size_crores": issue_size,
            "qib_subscription": qib_sub,
            "nii_subscription": nii_sub,
            "rii_subscription": rii_sub,
            "total_subscription": total_sub,
            "grey_market_premium_pct": gmp_pct,
            "pe_ratio": pe_ratio,
            "industry_pe": ind_pe,
        }
        with st.spinner("Synthesizing subscription signals and peer multiples..."):
            ipo_res = client.get_ipo_analysis(payload)

        i1, i2, i3, i4 = st.columns(4)
        i1.metric("Issue Price", f"${ipo_res['issue_price']:.2f}")
        i2.metric("Expected Listing Price", f"${ipo_res['expected_listing_price']:.2f}", f"+{ipo_res['expected_listing_gain_pct']:.1f}%")
        i3.metric("Bearish Listing Floor (5th %ile)", f"${ipo_res['bear_listing_price_q05']:.2f}")
        i4.metric("Bullish Listing Bound (95th %ile)", f"${ipo_res['bull_listing_price_q95']:.2f}")

        st.subheader("Documented Assumptions & Disclaimers")
        for a in ipo_res["assumptions"]:
            st.info(f"📌 {a}")
        for lim in ipo_res["limitations"]:
            st.warning(f"⚠️ {lim}")
