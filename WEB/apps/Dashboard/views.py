
# -- VIEWS ------------------------------------------------------------------- #

from django.views import View
from django.views import generic
from django.contrib import messages
from django.shortcuts import render, redirect

# ---------------------------------------------------------------------------- #

''' CLASE: Inicio de sesión '''
class LoginView(View):
    template_name = 'signin.html'
    context = { }

    def get(self, request):
        return render(request, self.template_name, self.context)

    def post(self, request):
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        # Datitos de prueba para el Selenium:
        VALID_USERNAME = "Ed"
        VALID_PASSWORD = "Caraphernelia"

        if username == VALID_USERNAME and password == VALID_PASSWORD:
            request.session['auth_user'] = username
            return redirect('dashboard:Home')

        messages.error(request, "Credenciales incorrectas. Intente nuevamente.")
        return render(request, self.template_name, self.context)

# ---------------------------------------------------------------------------- #

''' CLASE: Inicio (Dashboard) '''
class HomeView(View):
    template_name = 'dashboard/home.html'
    context = { }

    def get(self, request):
        return render(request, self.template_name, self.context)

# ---------------------------------------------------------------------------- #