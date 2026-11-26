import json
import os
import subprocess
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from algoritmos.a_estrella import buscar_a_estrella, calcular_heuristica_euclidiana
from algoritmos.bfs import buscar_bfs
from algoritmos.dfs import buscar_dfs
from algoritmos.dijkstra import buscar_dijkstra
from datos.generador_redes import generar_red_urbana
from datos.prueba_8 import cargar_red_8
from datos.prueba_12 import cargar_red_12
from estructuras.cola_fifo import ColaFIFO
from estructuras.grafo_ponderado import GrafoPonderado
from estructuras.min_heap import MinHeap
from estructuras.pila_lifo import PilaLIFO
from estadisticas.trafico import generar_estadisticas_trafico


PSEUDOCODIGOS = {
    "dfs": [
        "DFS(G, inicio, meta):",
        "  pila ← PilaLIFO(); pila.apilar(inicio)",
        "  mientras no pila.esta_vacia():",
        "    actual ← pila.desapilar()",
        "    si actual == meta: retornar ruta",
        "    si actual no en visitados: marcar visitado",
        "    para cada vecino v en G.vecinos(actual):",
        "      si v no en visitados: pila.apilar(v)",
    ],
    "bfs": [
        "BFS(G, inicio, meta):",
        "  cola ← ColaFIFO(); cola.encolar(inicio)",
        "  visitados.agregar(inicio)",
        "  mientras no cola.esta_vacia():",
        "    actual ← cola.desencolar()",
        "    si actual == meta: retornar ruta",
        "    para cada vecino v en G.vecinos(actual):",
        "      si v no en visitados: encolar(v)",
    ],
    "dijkstra": [
        "DIJKSTRA(G, inicio, meta):",
        "  dist[inicio] ← 0; heap.insertar(0, inicio)",
        "  mientras no heap.esta_vacia():",
        "    (d, actual) ← heap.extraer_min()",
        "    si actual == meta: retornar ruta",
        "    para cada arista (actual, v, peso):",
        "      nuevo ← d + peso",
        "      si nuevo < dist[v]: dist[v] ← nuevo; insertar",
    ],
    "a_estrella": [
        "A-STAR(G, inicio, meta):",
        "  g[inicio] ← 0; heap.insertar(h(inicio), inicio)",
        "  mientras no heap.esta_vacia():",
        "    (f, actual) ← heap.extraer_min()",
        "    si actual == meta: retornar ruta",
        "    para cada arista (actual, v, peso):",
        "      tentativo_g ← g[actual] + peso",
        "      si tentativo_g < g[v]: f ← tentativo_g + h(v); insertar",
    ],
}


def _serializar_grafo(grafo):
    nodos = []
    for est in grafo.obtener_estaciones():
        x, y = grafo.obtener_coordenadas(est)
        nodos.append({"id": est, "x": x, "y": y})

    aristas = []
    for a in grafo.obtener_aristas_unicas():
        aristas.append({
            "origen": a.origen,
            "destino": a.destino,
            "peso": a.peso,
            "congestion": a.congestion,
        })

    stats = generar_estadisticas_trafico(grafo, top_k=5)
    return {
        "nodos": nodos,
        "aristas": aristas,
        "stats": {
            "total_tramos": stats["total_tramos"],
            "peso_promedio": stats["peso_promedio"],
            "congestion_promedio": stats["congestion_promedio"],
        },
    }


def _construir_grafo_desde_json(nodos_json, aristas_json):
    grafo = GrafoPonderado(dirigido=False)
    for n in nodos_json:
        grafo.agregar_estacion(n["id"], float(n["x"]), float(n["y"]))
    for a in aristas_json:
        grafo.agregar_conexion(
            a["origen"],
            a["destino"],
            float(a["peso"]),
            int(a.get("congestion", 40)),
        )
    return grafo


def _reconstruir(predecesores, origen, destino):
    ruta = []
    actual = destino
    while actual is not None:
        ruta.append(actual)
        actual = predecesores.get(actual)
    ruta.reverse()
    return ruta if ruta and ruta[0] == origen else []


def _generar_traza_dfs(grafo, origen, destino):
    pasos = []
    pila = PilaLIFO()
    pila_vista = []
    visitados = []
    aristas_arbol = []
    predecesores = {origen: None}

    pila.apilar((origen, None))
    pila_vista.append(origen)

    pasos.append({
        "linea": 1,
        "actual": origen,
        "arista_eval": None,
        "decision": "info",
        "mensaje": f"Inicio DFS: apilamos '{origen}' en PilaLIFO.",
        "visitados": list(visitados),
        "aristas_arbol": list(aristas_arbol),
        "estructura": list(pila_vista),
        "ruta_parcial": [origen],
    })

    while not pila.esta_vacia():
        actual, padre = pila.desapilar()
        pila_vista.pop()

        if actual in visitados:
            pasos.append({
                "linea": 3,
                "actual": actual,
                "arista_eval": [padre, actual] if padre else None,
                "decision": "no",
                "mensaje": f"❌ NO es por aquí ({padre} → {actual}): '{actual}' ya fue visitado antes.",
                "visitados": list(visitados),
                "aristas_arbol": list(aristas_arbol),
                "estructura": list(pila_vista),
                "ruta_parcial": _reconstruir(predecesores, origen, padre) if padre else [origen],
            })
            continue

        if padre is not None:
            predecesores[actual] = padre
            aristas_arbol.append([padre, actual])
        visitados.append(actual)
        ruta_actual = _reconstruir(predecesores, origen, actual)

        pasos.append({
            "linea": 5,
            "actual": actual,
            "arista_eval": [padre, actual] if padre else None,
            "decision": "si" if padre else "info",
            "mensaje": (
                f"✅ Avanzamos por ({padre} → {actual}). Ruta acumulada: {' → '.join(ruta_actual)}."
                if padre else f"Explorando vecinos desde '{origen}'."
            ),
            "visitados": list(visitados),
            "aristas_arbol": list(aristas_arbol),
            "estructura": list(pila_vista),
            "ruta_parcial": ruta_actual,
        })

        if actual == destino:
            pasos.append({
                "linea": 4,
                "actual": actual,
                "arista_eval": None,
                "decision": "meta",
                "mensaje": f"🎯 ¡Meta alcanzada! Ruta DFS ({len(ruta_actual)-1} saltos): {' → '.join(ruta_actual)}.",
                "visitados": list(visitados),
                "aristas_arbol": list(aristas_arbol),
                "estructura": list(pila_vista),
                "ruta_parcial": ruta_actual,
            })
            return pasos

        vecinos = grafo.obtener_vecinos(actual)
        nuevos = 0
        for arista in reversed(vecinos):
            v = arista.destino
            if v not in visitados:
                nuevos += 1
                pila.apilar((v, actual))
                pila_vista.append(v)
                pasos.append({
                    "linea": 7,
                    "actual": actual,
                    "arista_eval": [actual, v],
                    "decision": "si",
                    "mensaje": f"✅ SÍ es candidato ({actual} → {v}): '{v}' no está visitado, se apila en PilaLIFO.",
                    "visitados": list(visitados),
                    "aristas_arbol": list(aristas_arbol),
                    "estructura": list(pila_vista),
                    "ruta_parcial": ruta_actual,
                })
            else:
                pasos.append({
                    "linea": 7,
                    "actual": actual,
                    "arista_eval": [actual, v],
                    "decision": "no",
                    "mensaje": f"❌ NO es por aquí ({actual} → {v}): '{v}' ya está visitado.",
                    "visitados": list(visitados),
                    "aristas_arbol": list(aristas_arbol),
                    "estructura": list(pila_vista),
                    "ruta_parcial": ruta_actual,
                })

        if nuevos == 0:
            pasos.append({
                "linea": 2,
                "actual": actual,
                "arista_eval": None,
                "decision": "retroceso",
                "mensaje": f"↩️ Sin salida en '{actual}': DFS retrocede desapilando el siguiente nodo.",
                "visitados": list(visitados),
                "aristas_arbol": list(aristas_arbol),
                "estructura": list(pila_vista),
                "ruta_parcial": ruta_actual,
            })

    return pasos


def _generar_traza_bfs(grafo, origen, destino):
    pasos = []
    cola = ColaFIFO()
    cola_vista = []
    visitados = [origen]
    aristas_arbol = []
    predecesores = {origen: None}

    cola.encolar(origen)
    cola_vista.append(origen)

    pasos.append({
        "linea": 1,
        "actual": origen,
        "arista_eval": None,
        "decision": "info",
        "mensaje": f"Inicio BFS: encolamos '{origen}' en ColaFIFO.",
        "visitados": list(visitados),
        "aristas_arbol": list(aristas_arbol),
        "estructura": list(cola_vista),
        "ruta_parcial": [origen],
    })

    while not cola.esta_vacia():
        actual = cola.desencolar()
        cola_vista.pop(0)
        ruta_actual = _reconstruir(predecesores, origen, actual)

        pasos.append({
            "linea": 4,
            "actual": actual,
            "arista_eval": None,
            "decision": "info",
            "mensaje": f"Desencolamos '{actual}'. Camino hasta aquí: {' → '.join(ruta_actual)} ({len(ruta_actual)-1} saltos).",
            "visitados": list(visitados),
            "aristas_arbol": list(aristas_arbol),
            "estructura": list(cola_vista),
            "ruta_parcial": ruta_actual,
        })

        if actual == destino:
            pasos.append({
                "linea": 5,
                "actual": actual,
                "arista_eval": None,
                "decision": "meta",
                "mensaje": f"🎯 ¡Meta alcanzada! Menor número de paradas ({len(ruta_actual)-1} saltos): {' → '.join(ruta_actual)}.",
                "visitados": list(visitados),
                "aristas_arbol": list(aristas_arbol),
                "estructura": list(cola_vista),
                "ruta_parcial": ruta_actual,
            })
            return pasos

        for arista in grafo.obtener_vecinos(actual):
            v = arista.destino
            if v not in visitados:
                visitados.append(v)
                predecesores[v] = actual
                aristas_arbol.append([actual, v])
                cola.encolar(v)
                cola_vista.append(v)
                pasos.append({
                    "linea": 7,
                    "actual": actual,
                    "arista_eval": [actual, v],
                    "decision": "si",
                    "mensaje": f"✅ SÍ, es por aquí ({actual} → {v}): estación nueva, se encola en ColaFIFO.",
                    "visitados": list(visitados),
                    "aristas_arbol": list(aristas_arbol),
                    "estructura": list(cola_vista),
                    "ruta_parcial": _reconstruir(predecesores, origen, v),
                })
            else:
                pasos.append({
                    "linea": 7,
                    "actual": actual,
                    "arista_eval": [actual, v],
                    "decision": "no",
                    "mensaje": f"❌ NO es por aquí ({actual} → {v}): '{v}' ya fue visitado en un nivel anterior.",
                    "visitados": list(visitados),
                    "aristas_arbol": list(aristas_arbol),
                    "estructura": list(cola_vista),
                    "ruta_parcial": ruta_actual,
                })

    return pasos


def _generar_traza_dijkstra(grafo, origen, destino):
    pasos = []
    estaciones = grafo.obtener_estaciones()
    dist = {e: float("inf") for e in estaciones}
    dist[origen] = 0.0
    predecesores = {origen: None}
    cerrados = []
    aristas_arbol = []

    heap = MinHeap()
    heap.insertar(0.0, origen)
    heap_vista = [(0.0, origen)]

    pasos.append({
        "linea": 1,
        "actual": origen,
        "arista_eval": None,
        "decision": "info",
        "mensaje": f"Inicio Dijkstra: dist['{origen}'] = 0 km. Insertamos en MinHeap.",
        "visitados": list(cerrados),
        "aristas_arbol": list(aristas_arbol),
        "estructura": [f"{n} ({d} km)" for d, n in sorted(heap_vista)],
        "ruta_parcial": [origen],
    })

    while not heap.esta_vacia():
        d_actual, actual = heap.extraer_min()
        for idx_h, item_h in enumerate(heap_vista):
            if item_h == (d_actual, actual):
                heap_vista.pop(idx_h)
                break

        if d_actual > dist[actual]:
            continue

        cerrados.append(actual)
        ruta_actual = _reconstruir(predecesores, origen, actual)
        if len(ruta_actual) >= 2:
            par = [ruta_actual[-2], ruta_actual[-1]]
            if par not in aristas_arbol:
                aristas_arbol.append(par)

        pasos.append({
            "linea": 3,
            "actual": actual,
            "arista_eval": None,
            "decision": "info",
            "mensaje": f"MinHeap extrae '{actual}' ({d_actual} km). Ruta actual: {' → '.join(ruta_actual)}.",
            "visitados": list(cerrados),
            "aristas_arbol": list(aristas_arbol),
            "estructura": [f"{n} ({d} km)" for d, n in sorted(heap_vista)],
            "ruta_parcial": ruta_actual,
        })

        if actual == destino:
            pasos.append({
                "linea": 4,
                "actual": actual,
                "arista_eval": None,
                "decision": "meta",
                "mensaje": f"🎯 ¡Ruta óptima encontrada! Costo mínimo {round(dist[destino], 2)} km: {' → '.join(ruta_actual)}.",
                "visitados": list(cerrados),
                "aristas_arbol": list(aristas_arbol),
                "estructura": [f"{n} ({d} km)" for d, n in sorted(heap_vista)],
                "ruta_parcial": ruta_actual,
            })
            return pasos

        for arista in grafo.obtener_vecinos(actual):
            v = arista.destino
            nuevo = round(d_actual + arista.peso, 2)
            anterior = "∞" if dist[v] == float("inf") else f"{dist[v]} km"

            if nuevo < dist[v]:
                dist[v] = nuevo
                predecesores[v] = actual
                heap.insertar(nuevo, v)
                heap_vista.append((nuevo, v))
                pasos.append({
                    "linea": 7,
                    "actual": actual,
                    "arista_eval": [actual, v],
                    "decision": "si",
                    "mensaje": f"✅ SÍ, es por aquí ({actual} → {v}): {d_actual} + {arista.peso} = {nuevo} km mejora {anterior}.",
                    "visitados": list(cerrados),
                    "aristas_arbol": list(aristas_arbol),
                    "estructura": [f"{n} ({d} km)" for d, n in sorted(heap_vista)],
                    "ruta_parcial": _reconstruir(predecesores, origen, v),
                })
            else:
                pasos.append({
                    "linea": 7,
                    "actual": actual,
                    "arista_eval": [actual, v],
                    "decision": "no",
                    "mensaje": f"❌ NO es por aquí ({actual} → {v}): {nuevo} km no mejora la ruta hacia '{v}' ({anterior}).",
                    "visitados": list(cerrados),
                    "aristas_arbol": list(aristas_arbol),
                    "estructura": [f"{n} ({d} km)" for d, n in sorted(heap_vista)],
                    "ruta_parcial": ruta_actual,
                })

    return pasos


def _generar_traza_a_estrella(grafo, origen, destino):
    pasos = []
    estaciones = grafo.obtener_estaciones()
    g_score = {e: float("inf") for e in estaciones}
    g_score[origen] = 0.0
    predecesores = {origen: None}
    cerrados = []
    aristas_arbol = []

    h0 = round(calcular_heuristica_euclidiana(grafo, origen, destino), 2)
    heap = MinHeap()
    heap.insertar(h0, origen)
    heap_vista = [(h0, origen)]

    pasos.append({
        "linea": 1,
        "actual": origen,
        "arista_eval": None,
        "decision": "info",
        "mensaje": f"Inicio A*: g['{origen}']=0, distancia recta al destino h={h0} km.",
        "visitados": list(cerrados),
        "aristas_arbol": list(aristas_arbol),
        "estructura": [f"{n} (f={f})" for f, n in sorted(heap_vista)],
        "ruta_parcial": [origen],
    })

    while not heap.esta_vacia():
        f_actual, actual = heap.extraer_min()
        for idx_h, item_h in enumerate(heap_vista):
            if item_h == (f_actual, actual):
                heap_vista.pop(idx_h)
                break

        h_act = calcular_heuristica_euclidiana(grafo, actual, destino)
        if f_actual > g_score[actual] + h_act + 1e-6:
            continue

        cerrados.append(actual)
        ruta_actual = _reconstruir(predecesores, origen, actual)
        if len(ruta_actual) >= 2:
            par = [ruta_actual[-2], ruta_actual[-1]]
            if par not in aristas_arbol:
                aristas_arbol.append(par)

        pasos.append({
            "linea": 3,
            "actual": actual,
            "arista_eval": None,
            "decision": "info",
            "mensaje": f"MinHeap elige '{actual}' con menor f={f_actual}. Ruta: {' → '.join(ruta_actual)}.",
            "visitados": list(cerrados),
            "aristas_arbol": list(aristas_arbol),
            "estructura": [f"{n} (f={f})" for f, n in sorted(heap_vista)],
            "ruta_parcial": ruta_actual,
        })

        if actual == destino:
            pasos.append({
                "linea": 4,
                "actual": actual,
                "arista_eval": None,
                "decision": "meta",
                "mensaje": f"🎯 ¡Meta alcanzada con A*! {round(g_score[destino], 2)} km explorando solo {len(cerrados)} nodos: {' → '.join(ruta_actual)}.",
                "visitados": list(cerrados),
                "aristas_arbol": list(aristas_arbol),
                "estructura": [f"{n} (f={f})" for f, n in sorted(heap_vista)],
                "ruta_parcial": ruta_actual,
            })
            return pasos

        for arista in grafo.obtener_vecinos(actual):
            v = arista.destino
            tent_g = round(g_score[actual] + arista.peso, 2)
            anterior = "∞" if g_score[v] == float("inf") else f"{g_score[v]} km"

            if tent_g < g_score[v]:
                predecesores[v] = actual
                g_score[v] = tent_g
                h_v = round(calcular_heuristica_euclidiana(grafo, v, destino), 2)
                f_v = round(tent_g + h_v, 2)
                heap.insertar(f_v, v)
                heap_vista.append((f_v, v))
                pasos.append({
                    "linea": 7,
                    "actual": actual,
                    "arista_eval": [actual, v],
                    "decision": "si",
                    "mensaje": f"✅ SÍ, es por aquí ({actual} → {v}): g={tent_g} + h={h_v} → f={f_v} km.",
                    "visitados": list(cerrados),
                    "aristas_arbol": list(aristas_arbol),
                    "estructura": [f"{n} (f={f})" for f, n in sorted(heap_vista)],
                    "ruta_parcial": _reconstruir(predecesores, origen, v),
                })
            else:
                pasos.append({
                    "linea": 7,
                    "actual": actual,
                    "arista_eval": [actual, v],
                    "decision": "no",
                    "mensaje": f"❌ NO es por aquí ({actual} → {v}): g={tent_g} km no mejora {anterior}.",
                    "visitados": list(cerrados),
                    "aristas_arbol": list(aristas_arbol),
                    "estructura": [f"{n} (f={f})" for f, n in sorted(heap_vista)],
                    "ruta_parcial": ruta_actual,
                })

    return pasos


class ManejadorVisualizador(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _enviar_sin_cache(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")

    def _responder_json(self, payload):
        cuerpo = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self._enviar_sin_cache()
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if parsed.path == "/":
            ruta_html = os.path.join(os.path.dirname(__file__), "interfaz", "index.html")
            with open(ruta_html, "rb") as f:
                contenido = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self._enviar_sin_cache()
            self.send_header("Content-Length", str(len(contenido)))
            self.end_headers()
            self.wfile.write(contenido)

        elif parsed.path == "/api/red":
            tipo = params.get("tipo", ["8"])[0]
            if tipo == "8":
                grafo = cargar_red_8()
            elif tipo == "12":
                grafo = cargar_red_12()
            elif tipo == "vacio":
                grafo = GrafoPonderado(dirigido=False)
            else:
                n = int(tipo) if tipo.isdigit() else int(params.get("n", ["30"])[0])
                semilla = int(params.get("semilla", ["42"])[0])
                grafo = generar_red_urbana(n, semilla=semilla)

            self._responder_json(_serializar_grafo(grafo))

    def do_POST(self):
        if self.path == "/api/traza":
            longitud = int(self.headers.get("Content-Length", 0))
            datos = json.loads(self.rfile.read(longitud).decode("utf-8"))

            grafo = _construir_grafo_desde_json(datos["nodos"], datos["aristas"])
            origen = datos["origen"]
            destino = datos["destino"]
            algoritmo = datos["algoritmo"]

            generadores = {
                "dfs": _generar_traza_dfs,
                "bfs": _generar_traza_bfs,
                "dijkstra": _generar_traza_dijkstra,
                "a_estrella": _generar_traza_a_estrella,
            }
            pasos = generadores[algoritmo](grafo, origen, destino)

            comparativa = []
            for clave, nombre, func, unidad in [
                ("dfs", "DFS (PilaLIFO)", buscar_dfs, "saltos"),
                ("bfs", "BFS (ColaFIFO)", buscar_bfs, "saltos"),
                ("dijkstra", "Dijkstra (MinHeap)", buscar_dijkstra, "km"),
                ("a_estrella", "A* (MinHeap)", buscar_a_estrella, "km"),
            ]:
                t0 = time.perf_counter()
                ruta, costo, exp = func(grafo, origen, destino)
                us = round((time.perf_counter() - t0) * 1_000_000, 1)
                comparativa.append({
                    "clave": clave,
                    "nombre": nombre,
                    "costo": f"{costo} {unidad}" if ruta else "Sin ruta",
                    "explorados": exp,
                    "tiempo_us": us,
                })

            self._responder_json({
                "pseudocodigo": PSEUDOCODIGOS[algoritmo],
                "pasos": pasos,
                "comparativa": comparativa,
            })


def iniciar_ventana_emergente(puerto=8055):
    servidor = HTTPServer(("127.0.0.1", puerto), ManejadorVisualizador)
    url = f"http://127.0.0.1:{puerto}"
    print(f"Visualizador interactivo activo en {url} (Ctrl+C en terminal para cerrar)")

    try:
        subprocess.Popen(["cmd", "/c", "start", "msedge", f"--app={url}"])
    except Exception:
        webbrowser.open(url)

    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nVisualizador cerrado.")
        servidor.server_close()


if __name__ == "__main__":
    iniciar_ventana_emergente()