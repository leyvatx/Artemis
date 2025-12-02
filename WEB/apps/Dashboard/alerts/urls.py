from django.urls import path
from .views import AlertsListView

alerts = [
    path('alerts/', AlertsListView.as_view(), name='AlertsList'),
]
