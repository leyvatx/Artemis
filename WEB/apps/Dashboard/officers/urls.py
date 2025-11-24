
# -- URLS -------------------------------------------------------------------- #

from . import views
from django.urls import path

# ---------------------------------------------------------------------------- #

officers = [
    # Detalles de un determinado oficial.
    path('officers/<int:pk>/', views.OfficerDetailView.as_view(), name='OfficerDetail'),

    # Datos biométricos.
    path('officers/biometrics/', views.biometric_api, name='OfficerBiometrics'),

    # Listado de oficiales:
    path('officers/', views.OfficersListView.as_view(), name='OfficersList'),

    # Crear nuevo oficial:
    path('officers/create/', views.OfficersCreateView.as_view(), name='OfficersCreate'),

    # Actualizar oficial:
    path('officers/update/<int:pk>/', views.OfficersUpdateView.as_view(), name='OfficersUpdate'),

    # Eliminar oficial:
    path('officers/delete/<int:pk>/', views.OfficersDeleteView.as_view(), name='OfficersDelete'),
]

# ---------------------------------------------------------------------------- #