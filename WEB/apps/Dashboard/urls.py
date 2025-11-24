
# -- URLS -------------------------------------------------------------------- #

from django.urls import path
from .views import LoginView, LogoutView, HomeView

# URLs de secciones del Dashboard:
# from .analytics.urls import analytics
# from .events.urls import events
from .geolocation.urls import geolocation
from .officers.urls import officers
# from .reports.urls import reports

# ---------------------------------------------------------------------------- #

app_name = 'dashboard'

urlpatterns = [
    # Inicio de sesión: 
    path('login/', LoginView.as_view(), name='Login'),
    path('logout/', LogoutView.as_view(), name='Logout'),

    # Inicio:
    path('', HomeView.as_view(), name='Home'),

] + geolocation + officers

# ---------------------------------------------------------------------------- #