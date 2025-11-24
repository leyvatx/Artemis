
# -- VIEWS ------------------------------------------------------------------- #

import requests
from .endpoints import AUTH_ENDPOINTS
from .mixins import LoginRequiredMixin

from django.views import View
from django.contrib import messages
from django.shortcuts import render, redirect

# ---------------------------------------------------------------------------- #

''' CLASE: Inicio de sesión '''
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
            messages.error(request, 'Las credenciales de acceso introducidas son incorrectas.')
            return render(request, self.template_name, {})

        tarnished = response.json()

        if 'data' not in tarnished:
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
        return render(request, self.template_name, {})

# ---------------------------------------------------------------------------- #