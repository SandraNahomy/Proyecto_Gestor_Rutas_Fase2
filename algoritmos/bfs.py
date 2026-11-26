from estructuras.cola_fifo import ColaFIFO


def _reconstruir_ruta(predecesores, origen, destino):
    ruta = []
    actual = destino
    while actual is not None:
        ruta.append(actual)
        actual = predecesores.get(actual)
    ruta.reverse()
    return ruta if ruta and ruta[0] == origen else None


def buscar_bfs(grafo, origen, destino):
    """
    Búsqueda en Anchura (BFS) usando ColaFIFO propia en O(1).
    Retorna: (ruta, saltos, nodos_explorados)
    """
    if origen == destino:
        return [origen], 0, 1

    cola = ColaFIFO()
    cola.encolar(origen)

    visitados = {origen}
    predecesores = {origen: None}
    nodos_explorados = 0

    while not cola.esta_vacia():
        actual = cola.desencolar()
        nodos_explorados += 1

        if actual == destino:
            ruta = _reconstruir_ruta(predecesores, origen, destino)
            return ruta, len(ruta) - 1, nodos_explorados

        for arista in grafo.obtener_vecinos(actual):
            vecino = arista.destino
            if vecino not in visitados:
                visitados.add(vecino)
                predecesores[vecino] = actual
                cola.encolar(vecino)

    return None, float("inf"), nodos_explorados