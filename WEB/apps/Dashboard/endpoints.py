
# -- ENDPOINTS --------------------------------------------------------------- #

import os

BASE_URL = os.getenv('API_BASE_URL', 'http://127.0.0.1:8000')

# Autenticación:
AUTH_ENDPOINTS = {
    'LOGIN': f'{BASE_URL}/auth/login/',
    'REGISTER': f'{BASE_URL}/auth/register/',
}

# Datos generales:
DATA_ENDPOINTS = {
    'HOME': f'{BASE_URL}/supervisors/{{id}}/statistics/'
}

# Datos biométricos:
BIOMETRICS_ENDPOINTS = {
    # TODO: Cambiar esta URL (en espera de creación del Endpoint).
    'TARNISHED': f'{BASE_URL}/biometrics/{{id}}',
}

# Oficiales (por supervisor):
OFFICERS_ENDPOINTS = {
    'LIST': f'{BASE_URL}/supervisors/{{id}}/officers/',
    'CREATE': f'{BASE_URL}/users/',
    'TARNISHED': f'{BASE_URL}/users/{{id}}/',
    'ASSIGNMENTS': f'{BASE_URL}/supervisors/assignments/',
}

# Reportes:
REPORTS_ENDPOINTS = {
    'LIST': f'{BASE_URL}/reports/?supervisor={{id}}',
    'TARNISHED': f'{BASE_URL}/reports/?officer={{id}}',

    'CREATE': f'{BASE_URL}/reports/',
    'CINDER': f'{BASE_URL}/reports/{{id}}/',
}

# Alertas:
ALERTS_ENDPOINTS = {
    'LIST': f'{BASE_URL}/alerts/',
}

# Analytics y ML:
ANALYTICS_ENDPOINTS = {
    # Historical Data (Biometrics)
    'HISTORICAL_BPM': f'{BASE_URL}/biometrics/bpm/?officer={{id}}',
    
    # Anomaly Detection (ML Alerts)
    'ANOMALY_DETECTION': f'{BASE_URL}/biometrics/alerts/',
    'ANOMALY_BY_OFFICER': f'{BASE_URL}/biometrics/alerts/?officer={{id}}',
    'ALERT_ACKNOWLEDGE': f'{BASE_URL}/biometrics/alerts/{{id}}/acknowledge/',
    'ALERT_RESOLVE': f'{BASE_URL}/biometrics/alerts/{{id}}/resolve/',
    
    # ML Predictions
    'ML_PREDICTIONS': f'{BASE_URL}/biometrics/predictions/',
    'PREDICTIONS_BY_OFFICER': f'{BASE_URL}/biometrics/predictions/?officer={{id}}',
    
    # Recommendations
    'RECOMMENDATIONS': f'{BASE_URL}/recommendations/',
    'RECOMMENDATIONS_BY_OFFICER': f'{BASE_URL}/recommendations/?officer={{id}}',
}

# ---------------------------------------------------------------------------- #