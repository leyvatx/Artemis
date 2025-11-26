
# -- URLS -------------------------------------------------------------------- #

from django.urls import path
from .views import LoginView, LogoutView, HomeView

# Sección de análisis (URLs)
# from .analytics.urls import analytics

# Sección de geolocalización (URLs)
from .geolocation.urls import geolocation

# Sección de oficiales (URLs)
from .officers.urls import officers

# Sección de reportes (URLs)
from .reports.urls import reports

# ---------------------------------------------------------------------------- #

app_name = 'dashboard'

urlpatterns = [
    # Inicio de sesión: 
    path('login/', LoginView.as_view(), name='Login'),
    path('logout/', LogoutView.as_view(), name='Logout'),

    # Inicio:
    path('', HomeView.as_view(), name='Home'),

] + geolocation + officers + reports

# ---------------------------------------------------------------------------- #