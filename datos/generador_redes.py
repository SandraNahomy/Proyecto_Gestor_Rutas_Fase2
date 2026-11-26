import math
import random
from estructuras.grafo_ponderado import GrafoPonderado


def generar_red_urbana(num_estaciones, grado_promedio=3.33, semilla=42):
    """
    Genera una red urbana dispersa y 100% conexa con 'num_estaciones' nodos.
    Garantiza que peso(u, v) >= distancia_euclidiana(u, v) para admisibilidad de A*.
    """
    rng = random.Random(semilla)
    grafo = GrafoPonderado(dirigido=False)

    limite_plano = math.sqrt(num_estaciones) * 10.0
    nombres = [f"E{i}" for i in range(1, num_estaciones + 1)]

    for nombre in nombres:
        x = round(rng.uniform(0, limite_plano), 2)
        y = round(rng.uniform(0, limite_plano), 2)
        grafo.agregar_estacion(nombre, x, y)

    aristas_existentes = set()

    def _distancia(u, v):
        x1, y1 = grafo.obtener_coordenadas(u)
        x2, y2 = grafo.obtener_coordenadas(v)
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def _conectar(u, v):
        par = tuple(sorted((u, v)))
        if u != v and par not in aristas_existentes:
            aristas_existentes.add(par)
            dist = _distancia(u, v)
            factor_vial = rng.uniform(1.15, 1.65)
            peso = round(max(1.0, dist * factor_vial), 2)
            congestion = rng.randint(15, 95)
            grafo.agregar_conexion(u, v, peso, congestion)
            return True
        return False

    # 1. Garantizar conectividad total uniendo cada nodo con su vecino más cercano
    conectados = [nombres[0]]
    for est in nombres[1:]:
        mas_cercana = min(conectados, key=lambda c: _distancia(est, c))
        _conectar(est, mas_cercana)
        conectados.append(est)

    # 2. Agregar vías secundarias cercanas hasta alcanzar el grado promedio objetivo
    aristas_objetivo = max(len(aristas_existentes), int(round((num_estaciones * grado_promedio) / 2)))
    intentos = 0
    max_intentos = num_estaciones * 30

    while len(aristas_existentes) < aristas_objetivo and intentos < max_intentos:
        intentos += 1
        u = rng.choice(nombres)
        candidatos = sorted(nombres, key=lambda v: _distancia(u, v))[1:7]
        v = rng.choice(candidatos)
        _conectar(u, v)

    return grafo