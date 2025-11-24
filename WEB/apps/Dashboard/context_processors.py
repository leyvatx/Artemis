
# -- CONTEXT PROCESSORS ------------------------------------------------------ #

''' Contexto de sesión (información del usuario) '''
def session_context(request):
    return {'auth_user': request.session.get('auth_user')}

# ---------------------------------------------------------------------------- #