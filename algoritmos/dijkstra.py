from estructuras.min_heap import MinHeap


def _reconstruir_ruta(predecesores, origen, destino):
    ruta = []
    actual = destino
    while actual is not None:
        ruta.append(actual)
        actual = predecesores.get(actual)
    ruta.reverse()
    return ruta if ruta and ruta[0] == origen else None


def buscar_dijkstra(grafo, origen, destino):
    """
    Algoritmo de Dijkstra utilizando MinHeap propio.
    Complejidad temporal: O((|V| + |E|) log |V|)
    Retorna: (ruta, costo_total, nodos_explorados)
    """
    estaciones = grafo.obtener_estaciones()
    if origen not in estaciones or destino not in estaciones:
        return None, float("inf"), 0

    distancias = {est: float("inf") for est in estaciones}
    distancias[origen] = 0.0
    predecesores = {origen: None}

    heap = MinHeap()
    heap.insertar(0.0, origen)
    nodos_explorados = 0

    while not heap.esta_vacia():
        dist_actual, actual = heap.extraer_min()

        if dist_actual > distancias[actual]:
            continue

        nodos_explorados += 1

        if actual == destino:
            ruta = _reconstruir_ruta(predecesores, origen, destino)
            return ruta, round(distancias[destino], 2), nodos_explorados

        for arista in grafo.obtener_vecinos(actual):
            vecino = arista.destino
            nueva_dist = dist_actual + arista.peso

            if nueva_dist < distancias[vecino]:
                distancias[vecino] = nueva_dist
                predecesores[vecino] = actual
                heap.insertar(nueva_dist, vecino)

    return None, float("inf"), nodos_explorados