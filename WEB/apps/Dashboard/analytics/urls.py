
# -- URLS -------------------------------------------------------------------- #

from . import views
from django.urls import path

# ---------------------------------------------------------------------------- #

analytics = [
    path('analytics/', views.AnalyticsView.as_view(), name='Analytics'),
    path('analytics/historical-data/', views.HistoricalDataView.as_view(), name='HistoricalData'),
    path('analytics/anomaly-detection/', views.AnomalyDetectionView.as_view(), name='AnomalyDetection'),
    path('analytics/anomaly-detection/<int:alert_id>/<str:action>/', views.AnomalyActionView.as_view(), name='AnomalyAction'),
    path('analytics/ml-predictions/', views.MLPredictionsView.as_view(), name='MLPredictions'),
    path('analytics/recommendations/', views.RecommendationsView.as_view(), name='Recommendations'),
]

# ---------------------------------------------------------------------------- #