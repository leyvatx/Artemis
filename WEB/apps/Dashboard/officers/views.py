
# -- VIEWS ------------------------------------------------------------------- #

from django.views import generic
from django.shortcuts import render, redirect

# ---------------------------------------------------------------------------- #

# Obtiene la lista completa de oficiales:
def fetch_officers():

    # Datos obtenidos de la API:
    response = [
        { "id": 1001, "name": "Elena Gutiérrez", "plate_number": "P-4589", "range": "Capitán", "status": "Activo" },
        { "id": 1002, "name": "Ricardo López", "plate_number": "P-3210", "range": "Sargento", "status": "Activo" },
        { "id": 1003, "name": "Sofía Vargas", "plate_number": "P-9011", "range": "Agente", "status": "En servicio" },
        { "id": 1004, "name": "Javier Pérez", "plate_number": "P-1122", "range": "Teniente", "status": "Vacaciones" },
        { "id": 1005, "name": "Carmen Flores", "plate_number": "P-6733", "range": "Comisario", "status": "Activo" },
        { "id": 1006, "name": "Andrés Mendoza", "plate_number": "P-8844", "range": "Agente", "status": "En servicio" },
        { "id": 1007, "name": "Valeria Rojas", "plate_number": "P-5555", "range": "Sargento", "status": "Inactivo" },
        { "id": 1008, "name": "Miguel Torres", "plate_number": "P-0066", "range": "Agente", "status": "En servicio" },
        { "id": 1009, "name": "Laura Herrera", "plate_number": "P-2277", "range": "Mayor", "status": "Activo" },
        { "id": 1010, "name": "Diego Soto", "plate_number": "P-7888", "range": "Agente", "status": "Vacaciones" },
        { "id": 1011, "name": "Carolina Gil", "plate_number": "P-3399", "range": "Capitán", "status": "Activo" },
        { "id": 1012, "name": "Sergio Ruiz", "plate_number": "P-4400", "range": "Agente", "status": "En servicio" },
        { "id": 1013, "name": "Daniela Castro", "plate_number": "P-5511", "range": "Teniente", "status": "Activo" },
        { "id": 1014, "name": "Fernando Nieto", "plate_number": "P-6622", "range": "Agente", "status": "En servicio" },
        { "id": 1015, "name": "Paula Reyes", "plate_number": "P-7733", "range": "Sargento", "status": "Baja médica" },
        { "id": 1016, "name": "Gustavo Morales", "plate_number": "P-8844", "range": "Agente", "status": "Activo" },
        { "id": 1017, "name": "Silvia Cruz", "plate_number": "P-9955", "range": "Capitán", "status": "En servicio" },
        { "id": 1018, "name": "Alejandro Cano", "plate_number": "P-1066", "range": "Agente", "status": "Vacaciones" },
        { "id": 1019, "name": "Natalia Vega", "plate_number": "P-2177", "range": "Comisario", "status": "Activo" },
        { "id": 1020, "name": "Héctor Ponce", "plate_number": "P-3288", "range": "Agente", "status": "En servicio" }
    ]

    return response

# Busca un oficial por su ID:
def get_officer_by_id(pk):
    try:
        pk = int(pk)
    except ValueError:
        return None
        
    for officer in fetch_officers():
        if officer["id"] == pk:
            return officer
    return None

# ---------------------------------------------------------------------------- #

# Listado de oficiales:
class OfficersListView(generic.ListView):
    template_name = 'dashboard/officers/list.html'
    paginate_by = 8 # Paginación: ocho por página.
    context_object_name = 'officers'

    def get_queryset(self):
        officers = fetch_officers()

        query = self.request.GET.get("s", "").strip().lower()

        if query:
            officers = [
                o for o in officers
                if query in o["name"].lower()
                or query in o["plate_number"].lower()
            ]

        return officers

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("s", "")
        return context

# ---------------------------------------------------------------------------- #

# Creación/Registro de oficiales:
class OfficersCreateView(generic.View):
    template_name = 'dashboard/officers/create.html'

    def get(self, request, *args, **kwargs):
        context = { 'titleSection': 'Registrando oficial' }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        data = request.POST

        # Simulación:
        print('\nRegistrando nuevo oficial...')
        print(f"- Nombre: {data.get('name')}")
        print(f"- Placa: {data.get('plate_number')}")
        print(f"- Rango: {data.get('range')}")
        print(f"- Estado: {data.get('status')}")

        return redirect('dashboard:OfficersList')

# ---------------------------------------------------------------------------- #

# Actualización de oficiales:
class OfficersUpdateView(generic.View):
    template_name = 'dashboard/officers/update.html'

    def get(self, request, pk, *args, **kwargs):
        officer = get_officer_by_id(pk)

        if not officer: # Si no se encuentra, redirige a la lista:
            return redirect('dashboard:OfficersList')

        context = { 'titleSection': 'Actualizando oficial',
            'officer': officer # Rellena el FORM con los datos actuales.
        }

        return render(request, self.template_name, context)

    def post(self, request, pk, *args, **kwargs):
        data = request.POST

        # Simulación:
        print('\nActualizando oficial...')
        print(f"- Nombre: {data.get('name')}")
        print(f"- Placa: {data.get('plate_number')}")
        print(f"- Rango: {data.get('range')}")
        print(f"- Estado: {data.get('status')}")

        return redirect('dashboard:OfficersList')

# ---------------------------------------------------------------------------- #

# Eliminación de oficial:
class OfficersDeleteView(generic.View):
    template_name = 'dashboard/officers/delete.html'

    def get(self, request, pk, *args, **kwargs):
        officer = get_officer_by_id(pk)

        if not officer: # Si no se encuentra, redirige a la lista:
            return redirect('dashboard:OfficersList')
        
        context = { 'titleSection': 'Eliminando oficial',
            'officer': officer # Oficial a eliminar.
        }

        return render(request, self.template_name, context)

    def post(self, request, pk, *args, **kwargs):
        officer = get_officer_by_id(pk)

        if not officer: # Nuevament redireccionamos:
            return redirect('dashboard:OfficersList')

        # Simulación:
        print('\nEliminando oficial...')
        print(f"- Oficial: {officer.get('name')}")

        return redirect('dashboard:OfficersList')

# ---------------------------------------------------------------------------- #