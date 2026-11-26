import time
from algoritmos.a_estrella import buscar_a_estrella
from algoritmos.dijkstra import buscar_dijkstra
from datos.generador_redes import generar_red_urbana


def ejecutar_benchmarks(tamanos=(10, 50, 100, 200, 500), repeticiones=40):
    print("\n=== BENCHMARK COMPARATIVO: DIJKSTRA VS A* (PROMEDIO DE 40 EJECUCIONES) ===")
    print(f"{'Nodos |V|':<10} | {'Aristas |E|':<12} | {'Dijkstra (µs)':<15} | {'A* (µs)':<12} | {'Nodos Exp. Dijkstra':<20} | {'Nodos Exp. A*':<15}")
    print("-" * 98)

    resultados = []

    for n in tamanos:
        grafo = generar_red_urbana(n, grado_promedio=3.33, semilla=42)
        origen = "E1"
        destino = f"E{n}"

        # Medición de Dijkstra
        t0 = time.perf_counter()
        for _ in range(repeticiones):
            _, costo_d, exp_d = buscar_dijkstra(grafo, origen, destino)
        tiempo_d_us = ((time.perf_counter() - t0) / repeticiones) * 1_000_000

        # Medición de A*
        t0 = time.perf_counter()
        for _ in range(repeticiones):
            _, costo_a, exp_a = buscar_a_estrella(grafo, origen, destino)
        tiempo_a_us = ((time.perf_counter() - t0) / repeticiones) * 1_000_000

        aristas = grafo.cantidad_aristas()
        resultados.append((n, aristas, round(tiempo_d_us, 2), round(tiempo_a_us, 2), exp_d, exp_a))

        print(f"{n:<10} | {aristas:<12} | {tiempo_d_us:<15.2f} | {tiempo_a_us:<12.2f} | {exp_d:<20} | {exp_a:<15}")

    intentar_graficar(resultados)
    return resultados


def intentar_graficar(resultados):
    try:
        import matplotlib.pyplot as plt

        nodos = [r[0] for r in resultados]
        t_dijkstra = [r[2] for r in resultados]
        t_astar = [r[3] for r in resultados]
        exp_dijkstra = [r[4] for r in resultados]
        exp_astar = [r[5] for r in resultados]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8))

        ax1.plot(nodos, t_dijkstra, marker="o", linewidth=2, color="#dc2626", label="Dijkstra (MinHeap)")
        ax1.plot(nodos, t_astar, marker="s", linewidth=2, color="#059669", label="A* (MinHeap + Euclidiana)")
        ax1.set_title("Tiempo Real de Ejecución vs. Tamaño de Red")
        ax1.set_xlabel("Número de Estaciones |V|")
        ax1.set_ylabel("Tiempo Promedio (µs)")
        ax1.grid(True, linestyle="--", alpha=0.5)
        ax1.legend()

        ax2.plot(nodos, exp_dijkstra, marker="o", linewidth=2, color="#dc2626", label="Dijkstra (Expansión radial)")
        ax2.plot(nodos, exp_astar, marker="s", linewidth=2, color="#059669", label="A* (Búsqueda dirigida)")
        ax2.set_title("Nodos Explorados Antes de Hallar la Meta")
        ax2.set_xlabel("Número de Estaciones |V|")
        ax2.set_ylabel("Cantidad de Nodos Expandidos")
        ax2.grid(True, linestyle="--", alpha=0.5)
        ax2.legend()

        plt.tight_layout()
        plt.savefig("grafica_rendimiento_fase2.png", dpi=200)
        print("\nGráfica exportada exitosamente como: grafica_rendimiento_fase2.png")
    except ImportError:
        print("\nNota: Si deseas generar la imagen PNG automáticamente, instala matplotlib con: pip install matplotlib")


if __name__ == "__main__":
    ejecutar_benchmarks()