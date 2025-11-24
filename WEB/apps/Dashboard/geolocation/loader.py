
# -- LOADER ------------------------------------------------------------------ #

import pickle
from pathlib import Path

# ---------------------------------------------------------------------------- #

CURRENT_DIR = Path(__file__).resolve().parent # /apps/Dashboard
GRAPH_PATH = CURRENT_DIR.parent.parent.parent / 'data' / 'Tijuana.pkl'

_cached_graph = None  # Caché en memoria.

# ---------------------------------------------------------------------------- #

def load_graph():
    global _cached_graph

    # Comprueba si se encuentra en la caché:
    if _cached_graph is None:
        print('\n- Cargando grafo de OpenStreetMap...')

        # Validación:
        if not GRAPH_PATH.exists():
            print(f'- ERROR: No se ha encontrado el archivo... {GRAPH_PATH}')
            return None

        # Carga del archivo:
        with GRAPH_PATH.open('rb') as File:
            _cached_graph = pickle.load(File)

        print('- Grafo cargado con éxito.')

    return _cached_graph

# ---------------------------------------------------------------------------- #