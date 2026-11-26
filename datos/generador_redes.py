import math
import random
from estructuras.grafo_ponderado import GrafoPonderado


def generar_red_urbana(n: int, semilla: int = 42) -> GrafoPonderado:
    """
    Genera una red urbana conexa con distribución espacial ordenada
    (cuadrícula panorámica con ligera variación orgánica) para evitar
    que las estaciones se superpongan y garantizar vías limpias.
    """
    rng = random.Random(semilla)
    grafo = GrafoPonderado(dirigido=False)

    if n <= 0:
        return grafo

    # Cuadrícula panorámica (más ancha que alta, ideal para pantalla)
    columnas = math.ceil(math.sqrt(n * 1.45))
    filas = math.ceil(n / columnas)
    separacion = 20.0

    celdas = [(f, c) for f in range(filas) for c in range(columnas)]
    rng.shuffle(celdas)

    coordenadas = {}
    estaciones = []

    for i in range(n):
        nombre = f"E{i + 1}"
        fila, col = celdas[i]
        # Desplazamiento controlado dentro de su propia celda (nunca choca con vecinos)
        dx = rng.uniform(-0.22 * separacion, 0.22 * separacion)
        dy = rng.uniform(-0.22 * separacion, 0.22 * separacion)
        x = round((col + 0.5) * separacion + dx, 2)
        y = round((fila + 0.5) * separacion + dy, 2)

        grafo.agregar_estacion(nombre, x, y)
        coordenadas[nombre] = (x, y)
        estaciones.append(nombre)

    if n == 1:
        return grafo

    aristas_creadas = set()

    def conectar(u: str, v: str):
        if u == v:
            return
        par = tuple(sorted((u, v)))
        if par in aristas_creadas:
            return
        x1, y1 = coordenadas[u]
        x2, y2 = coordenadas[v]
        dist_recta = math.hypot(x2 - x1, y2 - y1)
        # Factor >= 1.05 para garantizar que la heurística euclidiana de A* sea admisible
        peso = round(max(1, dist_recta * rng.uniform(1.05, 1.32)))
        congestion = rng.randint(15, 85)
        grafo.agregar_conexion(u, v, peso, congestion)
        aristas_creadas.add(par)

    # 1. Conectar cada estación únicamente con sus 3 vecinos más cercanos (evita cruces largos)
    k_vecinos = 2 if n <= 6 else 3
    for u in estaciones:
        xu, yu = coordenadas[u]
        cercanos = sorted(
            (e for e in estaciones if e != u),
            key=lambda v: math.hypot(coordenadas[v][0] - xu, coordenadas[v][1] - yu),
        )
        for v in cercanos[:k_vecinos]:
            conectar(u, v)

    # 2. Garantizar que toda la red quede 100 % conectada uniendo componentes cercanas
    visitados = set()
    componentes = []
    for est in estaciones:
        if est not in visitados:
            comp = []
            cola = [est]
            visitados.add(est)
            while cola:
                actual = cola.pop(0)
                comp.append(actual)
                for arista in grafo.obtener_vecinos(actual):
                    if arista.destino not in visitados:
                        visitados.add(arista.destino)
                        cola.append(arista.destino)
            componentes.append(comp)

    while len(componentes) > 1:
        comp_a = componentes[0]
        mejor_par = None
        mejor_dist = float("inf")
        mejor_idx = 1

        for idx in range(1, len(componentes)):
            for u in comp_a:
                xu, yu = coordenadas[u]
                for v in componentes[idx]:
                    d = math.hypot(coordenadas[v][0] - xu, coordenadas[v][1] - yu)
                    if d < mejor_dist:
                        mejor_dist = d
                        mejor_par = (u, v)
                        mejor_idx = idx

        conectar(mejor_par[0], mejor_par[1])
        componentes[0].extend(componentes.pop(mejor_idx))

    return grafo