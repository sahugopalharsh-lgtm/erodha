# ERODHA — Quantitative Equity Forecasting & Jump-Diffusion Risk Engine

**ERODHA** is a financial analytics and stochastic decision-support platform designed for stock-price scenario forecasting, tail-risk assessment, and IPO valuation. It features a decoupled, mathematically validated quantitative engine, a Django REST Framework API, and an interactive Streamlit dashboard.

---

## 1. System Architecture

```text
erodha/
├── quant_engine/                  # Pure mathematical & stochastic core (Zero Django/Streamlit dependencies)
│   ├── data_validation.py         # Time-series integrity, monotonic ordering, positive price checks
│   ├── returns.py                 # Simple vs log returns, Itô drift correction, normality tests
│   ├── estimation.py              # Continuous diffusion & jump parameter calibration
│   ├── gbm.py                     # Geometric Brownian Motion simulation
│   ├── jump_diffusion.py          # Merton Jump-Diffusion exact simulation
│   ├── monte_carlo.py             # Vectorized simulation & quantile trajectory envelopes
│   ├── risk.py                    # Parametric & empirical VaR, Expected Shortfall, Drawdown
│   ├── validation.py              # Out-of-sample backtesting & Kupiec POF test
│   └── ipo_analysis.py            # IPO valuation & listing scenario engine
├── backend/                       # Django & Django REST Framework application
│   ├── manage.py
│   ├── config/                    # Django settings & routing
│   └── api/                       # Serializers, views, and REST endpoints
├── frontend/                      # Streamlit interactive analytical dashboard
│   ├── app.py                     # Streamlit frontend entrypoint
│   └── api_client.py              # Decoupled HTTP API client
├── tests/                         # Pytest automated test suite (31 unit & 6 API integration tests)
├── requirements.txt               # Pinned Python dependencies
└── README.md
```

---

## 2. Mathematical Models & Equations

### 2.1 Geometric Brownian Motion (GBM)
$$dS_t = \mu S_t dt + \sigma S_t dW_t$$

By Itô's Lemma:
$$S_{t+\Delta t} = S_t \exp\left[\left(\mu - \frac{1}{2}\sigma^2\right)\Delta t + \sigma \sqrt{\Delta t} Z\right], \quad Z \sim \mathcal{N}(0, 1)$$

### 2.2 Merton Jump-Diffusion
$$\frac{dS_t}{S_{t-}} = (\mu - \lambda \kappa)dt + \sigma dW_t + (J - 1)dN_t$$
where:
- $N_t \sim \text{Poisson}(\lambda t)$
- $\ln(J) \sim \mathcal{N}(m_J, \delta_J^2)$
- Drift compensator: $\kappa = \mathbb{E}[J - 1] = \exp\left(m_J + \frac{1}{2}\delta_J^2\right) - 1$

### 2.3 Value at Risk (VaR) & Expected Shortfall (ES)
For portfolio loss $L = -(V_T - V_0)$:
$$\text{VaR}_\alpha = \inf\{l : \mathbb{P}(L \le l) \ge \alpha\}$$
$$\text{ES}_\alpha = \mathbb{E}[L \mid L \ge \text{VaR}_\alpha]$$

---

## 3. How to Launch & Run Erodha

### 1. Run Automated Test Suites
```powershell
pytest
```

### 2. Start the Django REST Backend
```powershell
python backend/manage.py runserver 127.0.0.1:8000
```
- API Health Check: `http://127.0.0.1:8000/api/health/`
- API Market Data: `http://127.0.0.1:8000/api/market-data/?symbol=AAPL`

### 3. (Optional, legacy) React prototype — NOT part of this package
The React prototype is archived separately in `legacy_prototype/` and is not required. The Streamlit dashboard below is the primary UI.

### 3b. Previous React instructions
```powershell
npm run dev
```
- Open your browser at: **`http://localhost:5173`**
- Features: Full dark mode aesthetic, Merton Jump-Diffusion simulation, Monte Carlo path projection charts, interactive confidence cones, live stock analytics for Indian equities.

### 4. Alternative Streamlit Dashboard
```powershell
streamlit run frontend/app.py --server.port 8501
```
- Open your browser at: `http://localhost:8501`


---

## 4. Data & Calibration Notes (important for your report)

- **Real data by default.** If Yahoo Finance fails, the API now returns an error instead of silently inventing prices.
  For offline demos only: `set ERODHA_ALLOW_SYNTHETIC=1` (responses are flagged `is_synthetic: true`).
- **Indian tickers** need a suffix: `RELIANCE.NS`, `TCS.NS`, `INFY.NS` (NSE) or `.BO` (BSE).
- **Merton calibration** now uses maximum likelihood (`estimate_merton_mle`) with the threshold method as the starting point
  (`calibration: "threshold"` still available). On simulated data with known parameters, MLE recovers jump intensity and jump
  size noticeably better than thresholding, but with ~1-2 years of daily data jump parameters stay noisy; use 3-5 years.
- **Risk is horizon-aware.** Multi-day VaR/ES use overlapping h-day returns; the `/api/risk/` response also includes
  Monte Carlo VaR/ES under GBM and Merton so the effect of jumps on the tail is visible.
