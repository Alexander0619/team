import heapq

class Nodo:
    def __init__(self, nombre, g, h, padre=None):
        self.nombre = nombre
        self.g = g  # Coste desde el nodo inicial
        self.h = h  # Heurística estimada al objetivo
        self.f = g + h  # Función de evaluación f(n)
        self.padre = padre  # Nodo anterior en el camino

    def __lt__(self, otro):
        return self.f < otro.f

def a_estrella(inicio, objetivo, obtener_vecinos, heuristica):
    # Lista abierta (nodos a explorar)
    abierta = []
    # Lista cerrada (nodos ya explorados)
    cerrada = set()

    # Nodo inicial
    nodo_inicio = Nodo(inicio, 0, heuristica(inicio, objetivo))
    heapq.heappush(abierta, nodo_inicio)

    while abierta:
        # Extraemos el nodo con el menor valor de f(n)
        nodo_actual = heapq.heappop(abierta)
        
        # Si llegamos al objetivo, reconstruimos el camino
        if nodo_actual.nombre == objetivo:
            camino = []
            while nodo_actual:
                camino.append(nodo_actual.nombre)
                nodo_actual = nodo_actual.padre
            return camino[::-1]  # Devolver el camino invertido

        cerrada.add(nodo_actual.nombre)

        # Explorar vecinos
        for vecino, coste in obtener_vecinos(nodo_actual.nombre):
            if vecino in cerrada:
                continue

            g = nodo_actual.g + coste
            h = heuristica(vecino, objetivo)
            nodo_vecino = Nodo(vecino, g, h, nodo_actual)

            # Si el vecino no está en la lista abierta, lo agregamos
            if not any(vecino == n.nombre for n in abierta):
                heapq.heappush(abierta, nodo_vecino)
    
    return None  # No hay solución

# Ejemplo de cómo usar el algoritmo A*:
def obtener_vecinos(nodo):
    # Aquí se definen los vecinos de cada nodo, con sus respectivos costes
    grafo = {
        'A': [('B', 1), ('C', 4)],
        'B': [('A', 1), ('C', 2), ('D', 5)],
        'C': [('A', 4), ('B', 2), ('D', 1)],
        'D': [('B', 5), ('C', 1)],
    }
    return grafo.get(nodo, [])

def heuristica(nodo, objetivo):
    # Definimos una heurística simple basada en la distancia de Manhattan
    heuristicas = {
        'A': 7,
        'B': 6,
        'C': 2,
        'D': 0,
    }
    return heuristicas.get(nodo, float('inf'))

# Ejecutamos el algoritmo A*
camino = a_estrella('A', 'D', obtener_vecinos, heuristica)
print(f'Camino encontrado: {camino}')