import math
from estructuras.min_heap import MinHeap


def calcular_heuristica_euclidiana(grafo, nodo_a, nodo_b):
    """Calcula la distancia euclidiana h(n) en línea recta entre dos estaciones."""
    x1, y1 = grafo.obtener_coordenadas(nodo_a)
    x2, y2 = grafo.obtener_coordenadas(nodo_b)
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def _reconstruir_ruta(predecesores, origen, destino):
    ruta = []
    actual = destino
    while actual is not None:
        ruta.append(actual)
        actual = predecesores.get(actual)
    ruta.reverse()
    return ruta if ruta and ruta[0] == origen else None


def buscar_a_estrella(grafo, origen, destino):
    """
    Algoritmo A* (A-Star) guiado por distancia euclidiana usando MinHeap propio.
    Función de evaluación: f(n) = g(n) + h(n)
    Complejidad temporal: O((|V| + |E|) log |V|)
    Retorna: (ruta, costo_real_total, nodos_explorados)
    """
    estaciones = grafo.obtener_estaciones()
    if origen not in estaciones or destino not in estaciones:
        return None, float("inf"), 0

    g_score = {est: float("inf") for est in estaciones}
    g_score[origen] = 0.0
    predecesores = {origen: None}

    f_inicial = calcular_heuristica_euclidiana(grafo, origen, destino)
    heap = MinHeap()
    heap.insertar(f_inicial, origen)
    nodos_explorados = 0

    while not heap.esta_vacia():
        f_actual, actual = heap.extraer_min()

        # Ignorar entradas desactualizadas en el MinHeap
        if f_actual > g_score[actual] + calcular_heuristica_euclidiana(grafo, actual, destino) + 1e-9:
            continue

        nodos_explorados += 1

        if actual == destino:
            ruta = _reconstruir_ruta(predecesores, origen, destino)
            return ruta, round(g_score[destino], 2), nodos_explorados

        for arista in grafo.obtener_vecinos(actual):
            vecino = arista.destino
            tentativo_g = g_score[actual] + arista.peso

            if tentativo_g < g_score[vecino]:
                predecesores[vecino] = actual
                g_score[vecino] = tentativo_g
                f_score = tentativo_g + calcular_heuristica_euclidiana(grafo, vecino, destino)
                heap.insertar(f_score, vecino)

    return None, float("inf"), nodos_explorados