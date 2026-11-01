"""
Django REST Framework Serializers for Erodha API
================================================
Defensive input validation and output schema definitions.
"""

from rest_framework import serializers


class MarketDataRequestSerializer(serializers.Serializer):
    symbol = serializers.CharField(max_length=20, default="AAPL")
    period = serializers.ChoiceField(
        choices=["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
        default="1y"
    )


class ForecastRequestSerializer(serializers.Serializer):
    symbol = serializers.CharField(max_length=20, default="AAPL")
    s0 = serializers.FloatField(required=False, min_value=0.01)
    mu = serializers.FloatField(required=False)
    sigma = serializers.FloatField(required=False, min_value=0.0)
    horizon_days = serializers.IntegerField(default=252, min_value=5, max_value=1260)
    n_paths = serializers.IntegerField(default=5000, min_value=100, max_value=20000)
    seed = serializers.IntegerField(default=42, required=False)
    calibration = serializers.ChoiceField(choices=["mle", "threshold"], default="mle")

    # Merton specific parameters
    lam = serializers.FloatField(required=False, min_value=0.0)
    m_j = serializers.FloatField(required=False)
    delta_j = serializers.FloatField(required=False, min_value=0.0)


class RiskRequestSerializer(serializers.Serializer):
    symbol = serializers.CharField(max_length=20, default="AAPL")
    portfolio_value = serializers.FloatField(default=100000.0, min_value=1.0)
    confidence_level = serializers.FloatField(default=0.95, min_value=0.80, max_value=0.999)
    horizon_days = serializers.IntegerField(default=1, min_value=1, max_value=252)
    period = serializers.ChoiceField(choices=["1y", "2y", "5y", "max"], default="2y")
    n_paths = serializers.IntegerField(default=20000, min_value=1000, max_value=50000)
    seed = serializers.IntegerField(default=42, required=False)


class BacktestRequestSerializer(serializers.Serializer):
    symbol = serializers.CharField(max_length=20, default="AAPL")
    split_ratio = serializers.FloatField(default=0.80, min_value=0.50, max_value=0.95)
    n_paths = serializers.IntegerField(default=2000, min_value=500, max_value=10000)
    seed = serializers.IntegerField(default=42, required=False)


class IPOAnalysisRequestSerializer(serializers.Serializer):
    company_name = serializers.CharField(max_length=100, default="TechCorp IPO")
    symbol = serializers.CharField(max_length=20, default="TECH.IPO")
    issue_price_min = serializers.FloatField(default=450.0, min_value=1.0)
    issue_price_max = serializers.FloatField(default=500.0, min_value=1.0)
    issue_price_final = serializers.FloatField(default=500.0, min_value=1.0)
    lot_size = serializers.IntegerField(default=30, min_value=1)
    issue_size_crores = serializers.FloatField(default=1500.0, min_value=1.0)
    qib_subscription = serializers.FloatField(default=25.0, min_value=0.0)
    nii_subscription = serializers.FloatField(default=12.0, min_value=0.0)
    rii_subscription = serializers.FloatField(default=8.0, min_value=0.0)
    total_subscription = serializers.FloatField(default=18.5, min_value=0.0)
    grey_market_premium_pct = serializers.FloatField(default=35.0)
    pe_ratio = serializers.FloatField(default=32.0, min_value=0.0)
    industry_pe = serializers.FloatField(default=28.0, min_value=0.0)
