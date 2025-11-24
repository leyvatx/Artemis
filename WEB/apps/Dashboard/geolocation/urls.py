
# -- URLS -------------------------------------------------------------------- #

from . import views
from django.urls import path

# ---------------------------------------------------------------------------- #

geolocation = [
    path('geolocation/', views.GeolocationView.as_view(), name='Geolocation'),
    path('geolocation/data/', views.get_all_officers, name='GeolocationData'), 
]

# ---------------------------------------------------------------------------- #