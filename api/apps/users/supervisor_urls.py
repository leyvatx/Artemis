from django.urls import path
from .views import supervisor_alerts_view, supervisor_officers_view, supervisor_statistics_view

urlpatterns = [
    path('<int:supervisor_id>/alerts/', supervisor_alerts_view, name='supervisor-alerts'),
    path('<int:supervisor_id>/officers/', supervisor_officers_view, name='supervisor-officers'),
    path('<int:supervisor_id>/statistics/', supervisor_statistics_view, name='supervisor-statistics'),
]