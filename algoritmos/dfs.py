from estructuras.pila_lifo import PilaLIFO


def _reconstruir_ruta(predecesores, origen, destino):
    ruta = []
    actual = destino
    while actual is not None:
        ruta.append(actual)
        actual = predecesores.get(actual)
    ruta.reverse()
    return ruta if ruta and ruta[0] == origen else None


def buscar_dfs(grafo, origen, destino):
    """
    Búsqueda en Profundidad (DFS) usando PilaLIFO propia en O(1).
    Retorna: (ruta, saltos, nodos_explorados)
    """
    pila = PilaLIFO()
    pila.apilar((origen, None))

    visitados = set()
    predecesores = {}
    nodos_explorados = 0

    while not pila.esta_vacia():
        actual, padre = pila.desapilar()

        if actual not in visitados:
            visitados.add(actual)
            predecesores[actual] = padre
            nodos_explorados += 1

            if actual == destino:
                ruta = _reconstruir_ruta(predecesores, origen, destino)
                return ruta, len(ruta) - 1, nodos_explorados

            for arista in grafo.obtener_vecinos(actual):
                vecino = arista.destino
                if vecino not in visitados:
                    pila.apilar((vecino, actual))

    return None, float("inf"), nodos_explorados