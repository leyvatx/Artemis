
# -- VIEWS ------------------------------------------------------------------- #

import requests, random

from django.views import generic
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect

from apps.Dashboard.mixins import LoginRequiredMixin
from apps.Dashboard.endpoints import SUPERVISORS_ENDPOINTS

# ---------------------------------------------------------------------------- #

# Obtiene la lista completa de supervisores:
def fetch_supervisors(request):

    try: # Intenta realizar la petición POST a la API.
        API_URL = SUPERVISORS_ENDPOINTS['LIST']
        response = requests.get(API_URL)

        if response.status_code != 200:
            messages.error(request, 'Ha ocurrido un error al hacer la petición al servidor.')
            return []

        data = response.json()
        return data.get('supervisors', [])

    except requests.exceptions.ConnectionError:
        messages.error(request, 'No se ha podido conectar con el servidor.')
        return []

# Gestiona a un supervisor por su ID:
def manage_supervisor(request, supervisor_id):

    try: # Construcción de la URL de la API:
        API_URL = SUPERVISORS_ENDPOINTS['TARNISHED'].format(id=supervisor_id)
        response = requests.get(API_URL)
        
        if response.status_code == 200:
            responseJSON = response.json()

            if responseJSON.get('success'):
                return responseJSON.get('data')
            else:
                messages.warning(request, 'Ha ocurrido un error con la respuesta del servidor.')
        else:
            messages.error(request, 'No se ha encontrado registro alguno del usuario solicitado.')
            
    except requests.exceptions.RequestException:
        messages.error(request, 'No se ha podido conectar con el servidor.')

    return None

# ---------------------------------------------------------------------------- #

# Información detallada:
class SupervisorDetailView(LoginRequiredMixin, generic.View):
    template_name = 'dashboard/supervisors/detail.html'

    def get(self, request, pk, *args, **kwargs):
        supervisorId = pk # ID del supervisor consultado.
        supervisorData = manage_supervisor(request, supervisorId)

        if not supervisorData:
            messages.error(request, 'No se ha podido obtener la información del usuario solicitado.')
            return redirect('dashboard:supervisorsList')

        return render(request, self.template_name, { "supervisor": supervisorData })

# ---------------------------------------------------------------------------- #

# Actualización de oficiales:
class SupervisorUpdateView(LoginRequiredMixin, generic.View):
    template_name = 'dashboard/supervisors/update.html'

    def get(self, request, pk, *args, **kwargs):
        supervisor = manage_supervisor(request, pk)

        if not supervisor: # Validación inicial.
            return redirect('dashboard:Home')

        context = {  'titleSection': 'Actualizando información', 'supervisor': supervisor }
        return render(request, self.template_name, context)

    def post(self, request, pk, *args, **kwargs):

        # Recopilación de datos.
        updateData = {
            "name": request.POST.get('name'),
            "email": request.POST.get('email'),
        }

        updateFiles = {}
        if 'picture' in request.FILES:
            updateFiles['picture'] = (
                request.FILES['picture'].name,
                request.FILES['picture'],
                request.FILES['picture'].content_type
            )

        try: # Actualización de los datos del oficial.
            API_UPDATE = SUPERVISORS_ENDPOINTS['TARNISHED'].format(id=pk)
            responseUpdate = requests.patch(API_UPDATE, data=updateData, files=updateFiles)

            if responseUpdate.status_code in [200, 201]:
                messages.success(request, 'La información del usuario ha sido actualizada correctamente.')

                # Actualización de información en AUTH_USER (para el context_processor).
                supervisor = manage_supervisor(request, pk)
                auth_user = request.session.get('auth_user')

                if auth_user and str(auth_user.get('id')) == str(pk):
                    auth_user['name'] = supervisor.get('name')
                    auth_user['email'] = supervisor.get('email')
                    auth_user['picture'] = supervisor.get('picture')
                    request.session['auth_user'] = auth_user

                return redirect('dashboard:SupervisorDetail', pk=pk)
            else:
                try: # Parsear el JSON pa' los errores.
                    errors = responseUpdate.json()
                except ValueError:
                    errors = {}

                if 'email' in errors:
                    messages.error(request, 'La dirección de correo proporcionada pertenece a otro usuario')
                elif 'badge_number' in errors:
                    messages.error(request, 'El número de placa proporcionado pertenece a otro usuario')

                if not errors: # Para errores no especificados.
                    messages.error(request, 'Ha ocurrido un error al intentar actualizar la información.')

                context = { 'titleSection': 'Actualizando información', 'supervisor': updateData }
                return render(request, self.template_name, context)

        except requests.exceptions.RequestException:
            messages.error(request, 'No se ha podido conectar con el servidor.')
            return redirect('dashboard:Home')

# ---------------------------------------------------------------------------- #