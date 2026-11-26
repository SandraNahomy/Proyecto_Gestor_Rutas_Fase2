import time
from algoritmos.a_estrella import buscar_a_estrella
from algoritmos.bfs import buscar_bfs
from algoritmos.dfs import buscar_dfs
from algoritmos.dijkstra import buscar_dijkstra
from datos.generador_redes import generar_red_urbana
from datos.prueba_8 import cargar_red_8
from datos.prueba_12 import cargar_red_12
from estadisticas.trafico import generar_estadisticas_trafico
from visualizador import iniciar_ventana_emergente


def mostrar_comparativa(grafo, origen, destino):
    algoritmos = [
        ("BFS (ColaFIFO)", buscar_bfs, "saltos"),
        ("DFS (PilaLIFO)", buscar_dfs, "saltos"),
        ("Dijkstra (MinHeap)", buscar_dijkstra, "km"),
        ("A* (Heurística + MinHeap)", buscar_a_estrella, "km"),
    ]

    print(f"\n=== COMPARATIVA DE RUTAS: {origen} -> {destino} ===")
    print(f"{'Algoritmo':<27} | {'Costo':<11} | {'Explorados':<10} | {'Tiempo (µs)':<11} | Ruta")
    print("-" * 95)

    for nombre, funcion, unidad in algoritmos:
        t0 = time.perf_counter()
        ruta, costo, explorados = funcion(grafo, origen, destino)
        tiempo_us = round((time.perf_counter() - t0) * 1_000_000, 2)

        if ruta:
            secuencia = " -> ".join(ruta)
            costo_str = f"{costo} {unidad}"
        else:
            secuencia = "Sin conexión"
            costo_str = "N/A"

        print(f"{nombre:<27} | {costo_str:<11} | {explorados:<10} | {tiempo_us:<11} | {secuencia}")


def mostrar_reporte_trafico(grafo):
    stats = generar_estadisticas_trafico(grafo, top_k=5)
    print("\n=== ESTADÍSTICAS DE TRÁFICO (ORDENADO CON MERGESORT) ===")
    print(f"Total de tramos activos : {stats['total_tramos']}")
    print(f"Longitud promedio       : {stats['peso_promedio']} km")
    print(f"Congestión promedio     : {stats['congestion_promedio']} %")
    print("\nTop 5 tramos más congestionados:")
    for idx, tramo in enumerate(stats["tramos_criticos"], start=1):
        print(f"  {idx}. {tramo.origen} <-> {tramo.destino} | Distancia: {tramo.peso} km | Congestión: {tramo.congestion}%")


def menu_principal():
    grafo_actual = cargar_red_12()
    nombre_red = "Red Propia Urbana (12 estaciones: D1-D12)"

    while True:
        print("\n" + "=" * 60)
        print("  GESTOR DE RUTAS DE TRANSPORTE URBANO — FASE 2")
        print(f"  Red activa: {nombre_red}")
        print("=" * 60)
        print("1. Cambiar red (8 est. Guía / 12 est. Propia / Simulada N nodos)")
        print("2. Ver estaciones disponibles")
        print("3. Calcular y comparar ruta (BFS, DFS, Dijkstra y A*)")
        print("4. Ver estadísticas de tráfico y congestión (MergeSort)")
        print("5. Abrir visualizador gráfico interactivo (Ventana JavaScript)")
        print("0. Salir")

        opcion = input("\nSeleccione una opción: ").strip()

        if opcion == "1":
            print("\nRedes disponibles:")
            print("  [1] Red Estándar de Prueba de Escritorio (8 estaciones: A-H)")
            print("  [2] Red Principal Propia (12 estaciones: D1-D12)")
            print("  [3] Red Simulada Personalizada (N estaciones)")
            sub = input("Elija red: ").strip()

            if sub == "1":
                grafo_actual = cargar_red_8()
                nombre_red = "Red Estándar Guía (8 estaciones: A-H)"
            elif sub == "2":
                grafo_actual = cargar_red_12()
                nombre_red = "Red Propia Urbana (12 estaciones: D1-D12)"
            elif sub == "3":
                n = int(input("Ingrese número de estaciones (ej. 50 o 100): ").strip())
                grafo_actual = generar_red_urbana(n)
                nombre_red = f"Red Simulada ({n} estaciones: E1-E{n})"

        elif opcion == "2":
            estaciones = grafo_actual.obtener_estaciones()
            print(f"\nEstaciones ({len(estaciones)}): {', '.join(estaciones)}")

        elif opcion == "3":
            estaciones = grafo_actual.obtener_estaciones()
            print(f"\nEstaciones disponibles: {', '.join(estaciones)}")
            origen = input("Estación de origen : ").strip().upper()
            destino = input("Estación de destino: ").strip().upper()

            if origen not in estaciones or destino not in estaciones:
                print("Error: Una o ambas estaciones no existen en la red activa.")
            else:
                mostrar_comparativa(grafo_actual, origen, destino)

        elif opcion == "4":
            mostrar_reporte_trafico(grafo_actual)

        elif opcion == "5":
            iniciar_ventana_emergente()

        elif opcion == "0":
            print("Cerrando Gestor de Rutas. ¡Éxitos en la sustentación!")
            break
        else:
            print("Opción no válida. Intente nuevamente.")


if __name__ == "__main__":
    menu_principal()