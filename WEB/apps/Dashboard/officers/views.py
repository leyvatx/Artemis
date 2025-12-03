
# -- VIEWS ------------------------------------------------------------------- #

import random
import requests

from django.views import generic
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect

from apps.Dashboard.mixins import LoginRequiredMixin
from apps.Dashboard.endpoints import OFFICERS_ENDPOINTS, BIOMETRICS_ENDPOINTS, REPORTS_ENDPOINTS

# ---------------------------------------------------------------------------- #

# Obtiene la lista completa de oficiales:
def fetch_officers(request):
    auth_user = request.session.get('auth_user', {})
    supervisorId = auth_user.get('id') # ID del supervisor.

    # Validación previa:
    if not supervisorId:
        messages.error(request, 'No se han encontrado los datos del supervisor.')
        return []

    try: # Intenta realizar la petición POST a la API.
        API_URL = OFFICERS_ENDPOINTS['LIST'].format(id=supervisorId)
        response = requests.get(API_URL)

        if response.status_code != 200:
            messages.error(request, 'Ha ocurrido un error al hacer la petición al servidor.')
            return []

        data = response.json()
        return data.get('officers', [])

    except requests.exceptions.ConnectionError:
        messages.error(request, 'No se ha podido conectar con el servidor.')
        return []

# Gestiona a un oficial por su ID:
def manage_officer(request, officer_id):

    try: # Construcción de la URL de la API:
        API_URL = OFFICERS_ENDPOINTS['TARNISHED'].format(id=officer_id)
        response = requests.get(API_URL)
        
        if response.status_code == 200:
            responseJSON = response.json()

            if responseJSON.get('success'):
                return responseJSON.get('data')
            else:
                messages.warning(request, 'Ha ocurrido un error con la respuesta del servidor.')
        else:
            messages.error(request, 'No se ha encontrado registro alguno del oficial solicitado.')
            
    except requests.exceptions.RequestException:
        messages.error(request, 'No se ha podido conectar con el servidor.')

    return None

# ---------------------------------------------------------------------------- #

# Un pequeño estado 'previo' para simular continuidad.
LAST_BPM = 78
LAST_STRESS = 35

# Datos biométricos.
def biometric_api(request):
    officerId = int(request.GET.get("officer", 0))

    if officerId == 2:
        try: # Intenta obtener los datos de la API.
            API_URL = BIOMETRICS_ENDPOINTS['TARNISHED']
            response = requests.get(API_URL, timeout=5)

            if response.status_code == 200:
                data = response.json()

                if data.get('success'):
                    if data.get('data'):
                        latest_entry = data["data"][0]

                        if latest_entry['user_id'] == officerId:
                            bpm = round(latest_entry["value"])
                            created_at = latest_entry["created_at"]
                    else:
                        bpm = 0
                        created_at = None

                    # Cálculo real de estrés basado en BPM
                    stress = calculate_stress_from_bpm(bpm)
                    print("bpm", bpm, "\nstress", stress, "\ncreated_at", created_at)

                    return JsonResponse({
                        "bpm": bpm,
                        "stress": stress,
                        "created_at": created_at
                    })

        except requests.exceptions.RequestException:
            messages.error(request, 'No se ha podido conectar con el servidor.')

    # Los demás oficiales poseen datos simulados.
    bpm, stress = biometric_data()
    return JsonResponse({ "bpm": bpm, "stress": stress })

# Cálculo del estrés según BPM.
def calculate_stress_from_bpm(bpm: int) -> int:
    if bpm <= 0: return 0
    min_bpm, max_bpm = 60, 140
    normalized = (bpm - min_bpm) / (max_bpm - min_bpm)
    stress = int(max(5, min(100, normalized * 100)))

    return stress

# Simulación de datos.
def biometric_data():
    global LAST_BPM, LAST_STRESS

    # Variación suave en el estrés.
    stress_delta = random.gauss(0, 1.2)
    new_stress = LAST_STRESS + stress_delta

    # Suavizado para evitar saltos bruscos.
    new_stress = (new_stress * 0.8) + (LAST_STRESS * 0.2)
    new_stress = max(5, min(100, round(new_stress)))

    # Variación de BPM (relacionado al estrés).
    target_bpm = 60 + (new_stress * 0.85)
    bpm_delta = random.gauss(0, 1.8)
    new_bpm = target_bpm + bpm_delta

    # Suavizado.
    new_bpm = (new_bpm * 0.75) + (LAST_BPM * 0.25)
    new_bpm = max(55, min(145, round(new_bpm)))

    # Guardado de valores (para continuidad).
    LAST_BPM = new_bpm
    LAST_STRESS = new_stress

    return new_bpm, new_stress

# ---------------------------------------------------------------------------- #

# Información detallada:
class OfficerDetailView(LoginRequiredMixin, generic.View):
    template_name = 'dashboard/officers/detail.html'
    context = {}

    def get(self, request, pk, *args, **kwargs):
        officerId = pk # ID del oficial consultado.
        API_REPORTS = REPORTS_ENDPOINTS['TARNISHED'].format(id=officerId)

        officerData = manage_officer(request, officerId)
        response = requests.get(API_REPORTS)

        if not officerData:
            messages.error(request, 'No se ha podido obtener la información del oficial solicitado.')
            return redirect('dashboard:OfficersList')

        # Reportes:
        officerReports = []
        if response.status_code == 200:
            try:
                data = response.json()
                officerReports = data.get("data", [])
            except ValueError:
                messages.error(request, 'Ha ocurrido un error al procesar los reportes del oficial.')

        # Etiqueta de estado:
        officerStatus = officerData.get('status')
        if not officerStatus:
            officerData['status_label'] = 'Desconocido'
        else:
            officerData['status_label'] = {
                'Active': 'Activo',
                'Inactive': 'Inactivo',
                'Suspended': 'Suspendido',
                'OnLeave': 'Fuera de servicio'
            }.get(officerStatus, officerStatus)

        self.context = { "officer": officerData, "reports": officerReports }
        return render(request, self.template_name, self.context)

# ---------------------------------------------------------------------------- #

# Listado de oficiales:
class OfficersListView(LoginRequiredMixin, generic.ListView):
    template_name = 'dashboard/officers/list.html'
    paginate_by = 8 # Paginación: ocho por página.
    context_object_name = 'officers'

    def get_queryset(self):
        officers = fetch_officers(self.request)
        query = self.request.GET.get('s', '').strip().lower()

        # Sistemita de búsqueda:
        if query and officers:
            officers = [
                o for o in officers
                if query in o.get('name', '').lower()
                or query in o.get('badge_number', '').lower()
            ]

        return officers

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('s', '')
        return context

# ---------------------------------------------------------------------------- #

# Creación/Registro de oficiales:
class OfficersCreateView(LoginRequiredMixin, generic.View):
    template_name = 'dashboard/officers/create.html'

    def get(self, request, *args, **kwargs):
        context = { 'titleSection': 'Registrando oficial' }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        auth_user = request.session.get('auth_user', {})
        supervisorId = auth_user.get('id')
        
        if not supervisorId:
            messages.error(request, 'Sesión inválida. Vuelva a iniciar sesión.')
            return redirect('dashboard:Logout')

        # Recopilación de datos para el registro del oficial.
        officerData = {
            "name": request.POST.get('name'),
            "email": request.POST.get('email'),
            "badge_number": request.POST.get('badge_number'),
            "rank": request.POST.get('rank'),
            "status": request.POST.get('status', 'Active'),
            "role": 2 # Dado que se estará creando un oficial se usará el ID de su respectivo rol.
        }

        officerFiles = {}
        if 'picture' in request.FILES:
            officerFiles['picture'] = (
                request.FILES['picture'].name,
                request.FILES['picture'],
                request.FILES['picture'].content_type
            )

        try: # Creación & asignación del oficial.
            API_CREATE = OFFICERS_ENDPOINTS['CREATE'].format(id=supervisorId)
            responseCreate = requests.post(API_CREATE, data=officerData, files=officerFiles)

            if responseCreate.status_code not in [200, 201]:       
                responseCreateJSON = responseCreate.json()

                error_context = {
                    'titleSection': 'Registrando oficial',
                    'officer_data': officerData # Datos del formulario.
                }

                if responseCreateJSON.get('role'): # En caso de que no se registrase un rol.
                    messages.error(request, 'No existe un nivel de usuario para los oficiales.')
              
                if responseCreateJSON.get('badge_number'):
                    messages.error(request, 'El número de placa introducido pertenece a otro oficial.')

                if responseCreateJSON.get('email'):
                    messages.error(request, 'La dirección de correo introducida pertenece a otro oficial.')

                return render(request, self.template_name, error_context)

            responseCreateJSON = responseCreate.json()
            newOfficerData = responseCreateJSON.get('data', {}) 
            newOfficerID = newOfficerData.get('id')

            if newOfficerID: # Asignación al supervisor.
                assignmentData = {
                    "supervisor": int(supervisorId),
                    "officer": int(newOfficerID),
                    "notes": "Asignación creada desde la aplicación WEB... Añiah ñiah ñiah."
                }

                API_ASSIGN = OFFICERS_ENDPOINTS['ASSIGNMENTS']
                responseAssign = requests.post(API_ASSIGN, json=assignmentData)

                if responseAssign.status_code in [200, 201]:
                    messages.success(request, f"El oficial '{officerData['name']}' ha sido registrado correctamente.")
                else:
                    messages.warning(request, 'Ha ocurrido un error en la asignación del oficial.')

            return redirect('dashboard:OfficersList')

        except requests.exceptions.RequestException:
            messages.error(request, 'No se ha podido conectar con el servidor.')
            
            context = {
                'titleSection': 'Registrando oficial',
                'officer_data': officerData # Datos del formulario.
            }

            return render(request, self.template_name, context)

# ---------------------------------------------------------------------------- #

# Actualización de oficiales:
class OfficersUpdateView(LoginRequiredMixin, generic.View):
    template_name = 'dashboard/officers/update.html'

    def get(self, request, pk, *args, **kwargs):
        officer = manage_officer(request, pk)

        if not officer: # Validación inicial.
            return redirect('dashboard:OfficersList')

        context = {  'titleSection': 'Actualizando oficial', 'officer': officer }
        return render(request, self.template_name, context)

    def post(self, request, pk, *args, **kwargs):

        # Recopilación de datos.
        updateData = {
            "name": request.POST.get('name'),
            "email": request.POST.get('email'),
            "badge_number": request.POST.get('badge_number'),
            "rank": request.POST.get('rank'),
            "status": request.POST.get('status'),
        }

        updateFiles = {}
        if 'picture' in request.FILES:
            updateFiles['picture'] = (
                request.FILES['picture'].name,
                request.FILES['picture'],
                request.FILES['picture'].content_type
            )

        try: # Actualización de los datos del oficial.
            API_UPDATE = OFFICERS_ENDPOINTS['TARNISHED'].format(id=pk)
            responseUpdate = requests.patch(API_UPDATE, data=updateData, files=updateFiles)

            if responseUpdate.status_code in [200, 201]:
                messages.success(request, 'La información del oficial ha sido actualizada correctamente.')
                return redirect('dashboard:OfficersList')
            else: 
                try: # Parsear el JSON pa' los errores.
                    errors = responseUpdate.json()
                except ValueError:
                    errors = {}

                if 'email' in errors:
                    messages.error(request, 'La dirección de correo proporcionada pertenece a otro oficial')
                elif 'badge_number' in errors:
                    messages.error(request, 'El número de placa proporcionado pertenece a otro oficial')

                if not errors: # Para errores no especificados.
                    messages.error(request, 'Ha ocurrido un error al intentar actualizar la información.')

                context = { 'titleSection': 'Actualizando oficial', 'officer': updateData }
                return render(request, self.template_name, context)

        except requests.exceptions.RequestException:
            messages.error(request, 'No se ha podido conectar con el servidor.')
            return redirect('dashboard:OfficersList')

# ---------------------------------------------------------------------------- #

# Eliminación de oficial:
class OfficersDeleteView(LoginRequiredMixin, generic.View):
    template_name = 'dashboard/officers/delete.html'

    def get(self, request, pk, *args, **kwargs):
        officer = manage_officer(request, pk)

        if not officer: # Si no se encuentra, redirige a la lista:
            return redirect('dashboard:OfficersList')
        
        context = { 'titleSection': 'Eliminando oficial', 'officer': officer }
        return render(request, self.template_name, context)

    def post(self, request, pk, *args, **kwargs):

        try: # URL para la eliminación:
            API_DELETE = OFFICERS_ENDPOINTS['TARNISHED'].format(id=pk)
            response = requests.delete(API_DELETE)

            if response.status_code in [200, 204]:
                messages.success(request, 'El oficial ha sido eliminado correctamente.')
            else:
                messages.error(request, 'Ha ocurrido un error con la eliminación. Intente nuevamente.')

        except requests.exceptions.RequestException:
            messages.error(request, 'No se ha podido conectar con el servidor.')

        return redirect('dashboard:OfficersList')

# ---------------------------------------------------------------------------- #