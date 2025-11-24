
# -- VIEWS ------------------------------------------------------------------- #

import random
from .loader import load_graph
from apps.Dashboard.mixins import LoginRequiredMixin
from apps.Dashboard.officers.views import fetch_officers

from django.views import View
from django.shortcuts import render
from django.http import JsonResponse

# ---------------------------------------------------------------------------- #

''' CLASE: Geolocalización (de oficiales activos) '''
class GeolocationView(LoginRequiredMixin, View):
    template_name = 'dashboard/geolocation/map.html'
    context = { }

    def get(self, request):
        return render(request, self.template_name, self.context)

# ---------------------------------------------------------------------------- #

'''
    Lamentablemente el presupuesto y el tiempo de desarrollo son escasos.
    Por ello, se ha tomado la decisión de simular las coordenadas de los oficiales.

    - No hablo como creo, no pienso como debería, y todo continúa en una oscuridad indefensa.
'''

# Estado global en memoria:
officer_node_state = {} # { officer_id : node_id }

# ---------------------------------------------------------------------------- #

def node_lat(G, n):
    return G.nodes[n]["y"]

def node_lng(G, n):
    return G.nodes[n]["x"]

def neighbors_of(G, n):
    return list(G.neighbors(n))

# ---------------------------------------------------------------------------- #

def get_all_officers(request):

    # Grafo cargado una sola vez (cacheado)
    G = load_graph()

    if G is None: # Validación inicial.
        return JsonResponse({ 'error': 'Ha ocurrido un error al intentar cargar el grafo.' }, status=500)

    # Lista de nodos/intersecciones.
    NODES = list(G.nodes)

    if not NODES:
        return JsonResponse({ 'error': 'El grafo no posee nodos.' }, status=500)

    # Oficiales actuales.
    officersAPI = fetch_officers(request)

    if not officersAPI:
        return JsonResponse({ 'error': 'No ha podido obtener el listado de oficiales.' }, status=500)

    STATUS_MAP = {
        'Active': 'Activo',
        'Inactive': 'Inactivo',
        'Suspended': 'Suspendido',
        'OnLeave': 'Fuera de servicio'
    }

    officers = []
    for raw in officersAPI:
        normalized_status = STATUS_MAP.get(raw.get('status'), 'Activo')

        officer = {
            "id": raw.get("id"),
            "name": raw.get("name"),
            "plate_number": raw.get("badge_number"),
            "range": raw.get("rank").capitalize() if raw.get("rank") else "",
            "status": normalized_status
        }

        officers.append(officer)

    result = []

    for officer in officers:

        # Filtrar oficiales no activos
        if officer['status'] not in ['Activo']:
            continue

        oid = officer['id']

        if oid not in officer_node_state:
            officer_node_state[oid] = random.choice(NODES)

        current = officer_node_state[oid]
        neighbors = neighbors_of(G, current)

        # Si por alguna razón un nodo no tiene vecinos, se reinicia.
        if not neighbors:
            current = random.choice(NODES)
            officer_node_state[oid] = current
            neighbors = neighbors_of(G, current)

        # Estado actualizado.
        next_node = random.choice(neighbors)
        officer_node_state[oid] = next_node

        lat = node_lat(G, next_node)
        lng = node_lng(G, next_node)

        # Estructura final del oficial (JSON).
        entry = officer.copy()
        entry["lat"] = lat
        entry["lng"] = lng

        result.append(entry)

    return JsonResponse(result, safe=False)

# ---------------------------------------------------------------------------- #