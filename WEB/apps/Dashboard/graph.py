
# -- GRAPH ------------------------------------------------------------------- #

# Importaciones:
import pickle
import osmnx as ox

# ---------------------------------------------------------------------------- #

# Configuración:
ox.settings.use_cache = True
ox.settings.log_console = True
ox.settings.timeout = 180

# ---------------------------------------------------------------------------- #

# Búsqueda:
query = { 'county': 'Tijuana', 'state': 'Baja California', 'country': 'Mexico' }
print(f'\n- Iniciando búsqueda: {query}...')

try: # Descarga:
    print(f'\n- Descargando la red vial del municipio...')
    Graph = ox.graph_from_place(query, network_type='drive', simplify=True, retain_all=False)

    # Guardado en PKL:
    file_path = 'Tijuana.pkl'
    with open(file_path, 'wb') as File:
        pickle.dump(Graph, File)

    print(f'\n- Grafo guardado con éxito: {file_path}')
    print(f'    - Nodos (intersecciones): {len(Graph.nodes)}')
    print(f'    - Aristas (calles): {len(Graph.edges)}')

except Exception as error:
    print(f'\nERROR: {error}')

# ---------------------------------------------------------------------------- #