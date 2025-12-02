
# -- URLS -------------------------------------------------------------------- #

from . import views
from django.urls import path

# ---------------------------------------------------------------------------- #

officers = [
    path('officers/biometrics/', views.biometric_api, name='OfficerBiometrics'),
    path('officers/create/', views.OfficersCreateView.as_view(), name='OfficersCreate'),
    path('officers/update/<int:pk>/', views.OfficersUpdateView.as_view(), name='OfficersUpdate'),
    path('officers/delete/<int:pk>/', views.OfficersDeleteView.as_view(), name='OfficersDelete'),
    path('officers/<int:pk>/', views.OfficerDetailView.as_view(), name='OfficerDetail'),
    path('officers/', views.OfficersListView.as_view(), name='OfficersList'),
]

# ---------------------------------------------------------------------------- #