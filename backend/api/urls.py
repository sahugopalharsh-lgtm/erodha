"""
API URL Routing for Erodha Backend.
"""

from django.urls import path
from api.views import (
    HealthCheckView,
    MarketDataView,
    ForecastGBMView,
    ForecastMertonView,
    RiskAnalysisView,
    BacktestView,
    IPOAnalysisView,
)

urlpatterns = [
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
