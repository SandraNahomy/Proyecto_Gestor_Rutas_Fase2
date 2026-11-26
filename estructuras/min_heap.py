class MinHeap:
    """Cola de Prioridad basada en Montículo Binario Mínimo (Min-Heap)."""
    def __init__(self):
        self._datos = []  # Lista interna de tuplas (prioridad, elemento)

    def esta_vacia(self):
        """Retorna True si el montículo está vacío. Complejidad: O(1)."""
        return len(self._datos) == 0

    def insertar(self, prioridad, elemento):
        """Inserta un par (prioridad, elemento) manteniendo la propiedad de mínimo. O(log n)."""
        self._datos.append((prioridad, elemento))
        self._flotar(len(self._datos) - 1)

    def extraer_min(self):
        """Extrae y retorna el par (prioridad, elemento) con menor prioridad. O(log n)."""
        if self.esta_vacia():
            raise IndexError("No se puede extraer: el MinHeap está vacío.")

        minimo = self._datos[0]
        ultimo = self._datos.pop()

        if not self.esta_vacia():
            self._datos[0] = ultimo
            self._hundir(0)

        return minimo

    def _flotar(self, indice):
        """Sube el elemento en 'indice' hasta restaurar el orden del Min-Heap."""
        while indice > 0:
            padre = (indice - 1) // 2
            if self._datos[indice][0] < self._datos[padre][0]:
                self._datos[indice], self._datos[padre] = self._datos[padre], self._datos[indice]
                indice = padre
            else:
                break

    def _hundir(self, indice):
        """Baja el elemento en 'indice' intercambiándolo con su hijo menor."""
        n = len(self._datos)
        while True:
            menor = indice
            izq = 2 * indice + 1
            der = 2 * indice + 2

            if izq < n and self._datos[izq][0] < self._datos[menor][0]:
                menor = izq
            if der < n and self._datos[der][0] < self._datos[menor][0]:
                menor = der

            if menor != indice:
                self._datos[indice], self._datos[menor] = self._datos[menor], self._datos[indice]
                indice = menor
            else:
                break

    def __len__(self):
        return len(self._datos)