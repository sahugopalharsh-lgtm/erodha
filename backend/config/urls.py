"""
Root URL Configuration for Erodha Backend.
"""
from django.urls import path, include

urlpatterns = [
    path('api/', include('api.urls')),
]
