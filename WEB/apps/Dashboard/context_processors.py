
# -- CONTEXT PROCESSORS ------------------------------------------------------ #

''' Contexto de sesión (información del usuario) '''
from django.conf import settings

def session_context(request):
    api_url = getattr(settings, 'API_BASE_URL', None) or 'http://127.0.0.1:8000/api'
    return {
        'auth_user': request.session.get('auth_user'),
        'api_base_url': api_url
    }

# ---------------------------------------------------------------------------- #