"""
API URL Routing for Erodha Backend.
"""

from django.urls import path, re_path
from api.views import (
    HealthCheckView,
    MarketDataView,
    ForecastGBMView,
    ForecastMertonView,
    RiskAnalysisView,
    BacktestView,
    IPOAnalysisView,
)

from api import v1_views as v1

urlpatterns = [
    # --- React dashboard API (real quant_engine, camelCase) ---
    re_path(r'^v1/stocks/?$', v1.StocksView.as_view()),
    re_path(r'^v1/stocks/(?P<symbol>[^/]+)/history/?$', v1.StockHistoryView.as_view()),
    re_path(r'^v1/stocks/(?P<symbol>[^/]+)/?$', v1.StockDetailView.as_view()),
    re_path(r'^v1/forecast/?$', v1.ForecastV1View.as_view()),
    re_path(r'^v1/simulations/monte-carlo/?$', v1.MonteCarloV1View.as_view()),
    re_path(r'^v1/risk/?$', v1.RiskV1View.as_view()),
    re_path(r'^v1/ipo/analyze/?$', v1.IpoV1View.as_view()),

    path('health/', HealthCheckView.as_view(), name='health'),
    path('v1/health', HealthCheckView.as_view(), name='v1-health'),
    path('v1/health/', HealthCheckView.as_view(), name='v1-health-slash'),
    path('market-data/', MarketDataView.as_view(), name='market-data'),
    path('forecast/gbm/', ForecastGBMView.as_view(), name='forecast-gbm'),
    path('forecast/merton/', ForecastMertonView.as_view(), name='forecast-merton'),
    path('risk/', RiskAnalysisView.as_view(), name='risk'),
    path('backtest/', BacktestView.as_view(), name='backtest'),
    path('ipo/', IPOAnalysisView.as_view(), name='ipo'),
]
