
# -- VIEWS ------------------------------------------------------------------- #

import requests
import logging
from .mixins import LoginRequiredMixin
from .endpoints import AUTH_ENDPOINTS, DATA_ENDPOINTS

from django.views import View
from django.contrib import messages
from django.shortcuts import render, redirect

# ---------------------------------------------------------------------------- #

''' CLASE: Inicio de sesión '''
logger = logging.getLogger(__name__)
class LoginView(View):
    template_name = 'signin.html'
    AUTH_URL = AUTH_ENDPOINTS['LOGIN']

    def get(self, request):
        if 'auth_user' in request.session:
            return redirect('dashboard:Home')
        return render(request, self.template_name, {})

    def post(self, request):
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        payload = { 'email': email, 'password': password }

        # Validación previa:
        if not email or not password:
            messages.error(request, 'Por favor, rellene todos los campos antes de continuar.')
            return render(request, self.template_name, {})

        try: # Intenta realizar la petición POST a la API.
            response = requests.post(self.AUTH_URL, json=payload)

        except requests.exceptions.ConnectionError:
            messages.error(request, 'No se ha podido conectar con el servidor de autenticación.')
            return render(request, self.template_name, {})

        if response.status_code != 200:
            try:
                logger.warning('Auth failed: %s %s', response.status_code, response.text)
            except Exception:
                logger.warning('Auth failed: status %s (no body)', response.status_code)

            messages.error(request, 'Las credenciales de acceso introducidas son incorrectas.')
            return render(request, self.template_name, {})

        tarnished = response.json()

        if 'data' not in tarnished:
            logger.warning('Auth response missing data key: %s', tarnished)
            messages.error(request, 'Respuesta inesperada del servidor de autenticación.')
            return render(request, self.template_name, {})

        user_data = tarnished['data']
        request.session['auth_user'] = user_data

        messages.success(request, f"¡Bienvenido, {user_data.get('name', 'mi estimado')}!")
        return redirect('dashboard:Home')

# ---------------------------------------------------------------------------- #

''' CLASE: Cierre de sesión '''
class LogoutView(View):

    def get(self, request):
        request.session.flush()
        messages.success(request, 'Nos vemos pronto, cuídate mucho.')
        return redirect('dashboard:Login')

# ---------------------------------------------------------------------------- #

''' CLASE: Inicio (Dashboard) '''
class HomeView(LoginRequiredMixin, View):
    template_name = 'dashboard/home.html'

    def get(self, request):
        auth_user = request.session.get('auth_user', {})
        supervisorId = auth_user.get('id')
        API_URL = DATA_ENDPOINTS['HOME'].format(id=supervisorId)

        response = requests.get(API_URL)
        data = response.json() if response.status_code == 200 else {}

        return render(request, self.template_name, data)

# ---------------------------------------------------------------------------- #

''' FUNCIÓN: 404 NOT FOUND '''
def not_found_404(request, exception):
    return render(request, '404.html', status=404)

# ---------------------------------------------------------------------------- #