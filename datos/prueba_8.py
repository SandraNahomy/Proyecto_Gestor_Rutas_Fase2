from estructuras.grafo_ponderado import GrafoPonderado


def cargar_red_8():
    """
    Carga la red estándar de 8 estaciones (A-H) y 11 conexiones de la guía
    para la prueba de escritorio y sustentación.
    """
    grafo = GrafoPonderado(dirigido=False)

    estaciones = {
        "A": (0.0, 0.0),
        "B": (2.0, 1.8),
        "C": (1.5, 1.0),
        "D": (6.0, 2.0),
        "E": (7.0, 0.5),
        "F": (9.5, 1.0),
        "G": (10.3, 1.0),
        "H": (12.0, 1.0),
    }

    for nombre, (x, y) in estaciones.items():
        grafo.agregar_estacion(nombre, x, y)

    # 11 conexiones oficiales de la guía (pesos en km/min)
    conexiones = [
        ("A", "C", 2, 45),
        ("A", "B", 4, 60),
        ("B", "D", 5, 70),
        ("B", "C", 1, 30),
        ("C", "E", 10, 85),
        ("C", "D", 8, 75),
        ("D", "F", 6, 65),
        ("D", "E", 2, 40),
        ("E", "F", 3, 50),
        ("F", "G", 1, 25),
        ("G", "H", 2, 35),
    ]

    for origen, destino, peso, congestion in conexiones:
        grafo.agregar_conexion(origen, destino, peso, congestion)

    return grafo