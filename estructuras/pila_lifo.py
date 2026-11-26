class NodoPila:
    """Nodo individual para la Pila LIFO."""
    def __init__(self, valor, siguiente=None):
        self.valor = valor
        self.siguiente = siguiente


class PilaLIFO:
    """Pila Last-In, First-Out (LIFO) con operaciones en O(1)."""
    def __init__(self):
        self._tope = None
        self._tamano = 0

    def esta_vacia(self):
        """Retorna True si la pila no tiene elementos. Complejidad: O(1)."""
        return self._tope is None

    def apilar(self, valor):
        """Inserta un elemento en el tope de la pila. Complejidad: O(1)."""
        self._tope = NodoPila(valor, self._tope)
        self._tamano += 1

    def desapilar(self):
        """Extrae y retorna el elemento del tope de la pila. Complejidad: O(1)."""
        if self.esta_vacia():
            raise IndexError("No se puede desapilar: la pila está vacía.")
        valor = self._tope.valor
        self._tope = self._tope.siguiente
        self._tamano -= 1
        return valor

    def __len__(self):
        return self._tamano