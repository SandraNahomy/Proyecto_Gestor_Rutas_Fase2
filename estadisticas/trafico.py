def ordenar_tramos_mergesort(tramos):
    """
    Ordena una lista de objetos Arista de mayor a menor nivel de congestión
    usando MergeSort propio (Divide y Vencerás).
    Recurrencia: T(n) = 2T(n/2) + O(n)  =>  Complejidad: O(n log n)
    """
    if len(tramos) <= 1:
        return tramos

    medio = len(tramos) // 2
    izquierda = ordenar_tramos_mergesort(tramos[:medio])
    derecha = ordenar_tramos_mergesort(tramos[medio:])

    return _mezclar(izquierda, derecha)


def _mezclar(izquierda, derecha):
    resultado = []
    i = 0
    j = 0

    while i < len(izquierda) and j < len(derecha):
        # Orden descendente: primero los tramos más congestionados
        if izquierda[i].congestion >= derecha[j].congestion:
            resultado.append(izquierda[i])
            i += 1
        else:
            resultado.append(derecha[j])
            j += 1

    resultado.extend(izquierda[i:])
    resultado.extend(derecha[j:])
    return resultado


def generar_estadisticas_trafico(grafo, top_k=5):
    """
    Analiza la red y retorna métricas de congestión junto con los
    top_k tramos más congestionados ordenados con MergeSort.
    """
    aristas = grafo.obtener_aristas_unicas()
    if not aristas:
        return {
            "total_tramos": 0,
            "peso_promedio": 0.0,
            "congestion_promedio": 0.0,
            "tramos_criticos": [],
        }

    tramos_ordenados = ordenar_tramos_mergesort(aristas)
    peso_total = sum(a.peso for a in aristas)
    congestion_total = sum(a.congestion for a in aristas)

    return {
        "total_tramos": len(aristas),
        "peso_promedio": round(peso_total / len(aristas), 2),
        "congestion_promedio": round(congestion_total / len(aristas), 2),
        "tramos_criticos": tramos_ordenados[:top_k],
    }