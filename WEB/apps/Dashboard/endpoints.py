
# -- ENDPOINTS --------------------------------------------------------------- #

BASE_URL = "http://127.0.0.1:8002" 

# Autenticación:
AUTH_ENDPOINTS = {
    'LOGIN': f'{BASE_URL}/auth/login/',
    'REGISTER': f'{BASE_URL}/auth/register/',
}

# Oficiales (por supervisor):
OFFICERS_ENDPOINTS = {
    'LIST': f'{BASE_URL}/supervisors/{{id}}/officers/',
    'CREATE': f'{BASE_URL}/users/',
    'TARNISHED': f'{BASE_URL}/users/{{id}}/',
    'ASSIGNMENTS': f'{BASE_URL}/supervisors/assignments/',
}

# Datos biométricos:
BIOMETRICS_ENDPOINTS = {
    # TODO: Cambiar esta URL (en espera de creación del Endpoint).
    'TARNISHED': f'{BASE_URL}/biometrics/{{id}}',
}

# Alertas:
ALERTS_ENDPOINTS = {
    'LIST': f'{BASE_URL}/alerts/',
}

# Eventos:
EVENTS_ENDPOINTS = {
    'CRUD': f'{BASE_URL}/events/',
}

# Reportes:
REPORTS_ENDPOINTS = {
    'CRUD': f'{BASE_URL}/reports/',
}

# ---------------------------------------------------------------------------- #