
# -- MIXINS ------------------------------------------------------------------ #

from django.contrib import messages
from django.shortcuts import redirect

# ---------------------------------------------------------------------------- #

''' Asegura la validación de inicio de sesión para el acceso a determinadas vistas. '''
class LoginRequiredMixin:

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('auth_user'):
            messages.warning(request, 'Por favor, inicie sesión para poder acceder a las funcionalidades del sistema.')
            return redirect('dashboard:Login')

        return super().dispatch(request, *args, **kwargs)

# ---------------------------------------------------------------------------- #