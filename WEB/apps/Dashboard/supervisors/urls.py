
# -- URLS -------------------------------------------------------------------- #

from . import views
from django.urls import path

# ---------------------------------------------------------------------------- #

supervisor = [
    path('me/<int:pk>/', views.SupervisorDetailView.as_view(), name='SupervisorDetail'),
    path('me/update/<int:pk>/', views.SupervisorUpdateView.as_view(), name='SupervisorUpdate'),
]

# ---------------------------------------------------------------------------- #