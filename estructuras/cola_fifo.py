class NodoCola:
    """Nodo individual para la lista enlazada de la Cola FIFO."""
    def __init__(self, valor):
        self.valor = valor
        self.siguiente = None


class ColaFIFO:
    """Cola First-In, First-Out (FIFO) con operaciones en O(1)."""
    def __init__(self):
        self._frente = None
        self._final = None
        self._tamano = 0

    def esta_vacia(self):
        """Retorna True si no hay elementos en la cola. Complejidad: O(1)."""
        return self._frente is None

    def encolar(self, valor):
        """Agrega un elemento al final de la cola. Complejidad: O(1)."""
        nuevo_nodo = NodoCola(valor)
        if self.esta_vacia():
            self._frente = nuevo_nodo
            self._final = nuevo_nodo
        else:
            self._final.siguiente = nuevo_nodo
            self._final = nuevo_nodo
        self._tamano += 1

    def desencolar(self):
        """Extrae y retorna el elemento del frente de la cola. Complejidad: O(1)."""
        if self.esta_vacia():
            raise IndexError("No se puede desencolar: la cola está vacía.")
        valor = self._frente.valor
        self._frente = self._frente.siguiente
        if self._frente is None:
            self._final = None
        self._tamano -= 1
        return valor

    def __len__(self):
        return self._tamano