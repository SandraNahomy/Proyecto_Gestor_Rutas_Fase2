class Arista:
    """Representa una conexión dirigida o tramo entre dos estaciones."""
    def __init__(self, origen, destino, peso, congestion=0):
        self.origen = origen
        self.destino = destino
        self.peso = float(peso)
        self.congestion = congestion  # Porcentaje o flujo vehicular (0 a 100)

    def __repr__(self):
        return f"Arista({self.origen} -> {self.destino}, peso={self.peso})"


class GrafoPonderado:
    """Grafo representado mediante Lista de Adyacencia con pesos y coordenadas."""
    def __init__(self, dirigido=False):
        self.dirigido = dirigido
        self._adyacencia = {}     # {estacion: [Arista, ...]}
        self._coordenadas = {}    # {estacion: (x, y)}

    def agregar_estacion(self, nombre, x=0.0, y=0.0):
        """Registra una estación (vértice) con sus coordenadas territoriales."""
        if nombre not in self._adyacencia:
            self._adyacencia[nombre] = []
        self._coordenadas[nombre] = (float(x), float(y))

    def agregar_conexion(self, origen, destino, peso, congestion=0):
        """Agrega una arista ponderada entre origen y destino."""
        if origen not in self._adyacencia:
            self.agregar_estacion(origen)
        if destino not in self._adyacencia:
            self.agregar_estacion(destino)

        self._adyacencia[origen].append(Arista(origen, destino, peso, congestion))
        if not self.dirigido:
            self._adyacencia[destino].append(Arista(destino, origen, peso, congestion))

    def obtener_vecinos(self, estacion):
        """Retorna la lista de objetos Arista salientes de la estación. O(1)."""
        return self._adyacencia.get(estacion, [])

    def obtener_coordenadas(self, estacion):
        """Retorna la tupla (x, y) de la estación. O(1)."""
        return self._coordenadas.get(estacion, (0.0, 0.0))

    def obtener_estaciones(self):
        """Retorna todas las estaciones registradas en el grafo."""
        return list(self._adyacencia.keys())

    def obtener_aristas_unicas(self):
        """Retorna una lista de tramos sin duplicados (útil para reportes de tráfico)."""
        aristas = []
        vistas = set()
        for origen, lista_aristas in self._adyacencia.items():
            for arista in lista_aristas:
                par = (origen, arista.destino) if self.dirigido else tuple(sorted((origen, arista.destino)))
                if par not in vistas:
                    vistas.add(par)
                    aristas.append(arista)
        return aristas

    def cantidad_vertices(self):
        return len(self._adyacencia)

    def cantidad_aristas(self):
        total = sum(len(vecinos) for vecinos in self._adyacencia.values())
        return total if self.dirigido else total // 2