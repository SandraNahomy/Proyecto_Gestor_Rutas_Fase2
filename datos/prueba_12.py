from estructuras.grafo_ponderado import GrafoPonderado


def cargar_red_12():
    """
    Reconstruye la red principal de 12 estaciones (D1-D12) y 20 aristas de la Fase 1,
    ampliada con pesos reales (km), coordenadas (x, y) y nivel de congestion (%).
    """
    grafo = GrafoPonderado(dirigido=False)

    # 1. Registro de las 12 estaciones con coordenadas territoriales (km)
    estaciones = {
        "D1":  (1.0, 9.0),  # Estación periférica noroccidental
        "D2":  (5.0, 7.0),  # Portal central norte
        "D3":  (1.0, 5.5),  # Corredor occidental
        "D4":  (4.5, 3.5),  # Portal central sur
        "D5":  (4.5, 9.0),  # Nodo de transferencia nororiental
        "D6":  (7.5, 7.5),  # Nodo de transferencia oriental superior
        "D7":  (8.5, 9.0),  # Estación de cierre circuito noreste
        "D8":  (8.5, 5.5),  # Nodo de enlace oriental inferior
        "D9":  (2.0, 2.5),  # Portal suroccidental
        "D10": (4.5, 1.5),  # Estación interna anillo sur
        "D11": (6.5, 2.0),  # Terminal sur de convergencia
        "D12": (9.5, 2.5),  # Estación periférica suroriental
    }

    for nombre, (x, y) in estaciones.items():
        grafo.agregar_estacion(nombre, x, y)

    # 2. Registro de las 20 conexiones bidireccionales exactas de Fase 1
    # Formato: (origen, destino, peso_km, congestion_porcentaje)
    # El orden mantiene la adyacencia exacta de D5 ['D2', 'D1', 'D6', 'D7']
    conexiones = [
        ("D2", "D5", 2.5, 65),
        ("D1", "D3", 4.0, 30),
        ("D1", "D5", 4.5, 40),
        ("D2", "D4", 4.0, 85),
        ("D2", "D6", 3.0, 70),
        ("D2", "D8", 4.5, 60),
        ("D3", "D9", 3.5, 35),
        ("D4", "D9", 3.0, 75),
        ("D4", "D10", 2.5, 50),
        ("D4", "D11", 3.0, 80),
        ("D5", "D6", 4.0, 55),
        ("D5", "D7", 4.5, 25),
        ("D6", "D7", 2.0, 30),
        ("D6", "D8", 2.5, 60),
        ("D7", "D8", 4.0, 35),
        ("D8", "D12", 3.5, 45),
        ("D9", "D10", 3.0, 40),
        ("D9", "D11", 5.0, 65),
        ("D10", "D11", 2.5, 45),
        ("D11", "D12", 3.5, 50),
    ]

    for origen, destino, peso, congestion in conexiones:
        grafo.agregar_conexion(origen, destino, peso, congestion)

    return grafo