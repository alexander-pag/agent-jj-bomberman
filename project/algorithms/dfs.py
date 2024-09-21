from agents import RockAgent, MetalAgent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def dfs(start, goal, model) -> list:
    """
    Implementa el algoritmo de búsqueda en profundidad (DFS) para encontrar un camino
    desde una posición inicial hasta una posición objetivo en un modelo de grid.

    Args:
        start: Tupla que representa la posición inicial.
        goal: Tupla que representa la posición objetivo.
        model: Modelo del entorno que contiene la información del grid y los agentes.

    Returns:
        Una lista de posiciones que representa el camino encontrado, o None si no existe camino.
    """

    # Movimiento en 4 direcciones (arriba, abajo, izquierda, derecha)
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    def is_valid_move(pos) -> bool:
        """
        Verifica si un movimiento es válido, es decir, si la posición resultante
        está dentro de los límites del grid y si la celda está libre de obstáculos.

        Args:
            pos: Tupla que representa la posición a verificar.

        Returns:
            bool: True si el movimiento es válido, False en caso contrario.
        """
        # Verificar si la posición está dentro de los límites del grid
        if model.grid.out_of_bounds(pos):
            return False

        # Revisar si la celda está libre de obstáculos
        cell_contents = model.grid.get_cell_list_contents([pos])
        for agent in cell_contents:
            if isinstance(agent, (RockAgent, MetalAgent)):
                return False
        return True

    # Pila para el recorrido DFS (almacena los nodos a visitar y el camino recorrido hasta ahora)
    stack = [(start, [start])]

    # Conjunto para almacenar las celdas visitadas
    visited = set()

    while stack:

        logger.info(f"Lista de nodos visitados: {visited}")
        logger.info(f"Pila de nodos: {stack}")

        current, path = stack.pop()

        # Si hemos alcanzado el objetivo, devolvemos el camino
        if current == goal:
            return path

        if current not in visited:
            visited.add(current)

            # Explorar vecinos
            for direction in directions:
                neighbor = (current[0] + direction[0], current[1] + direction[1])

                # Verificar si el movimiento es válido y si no hemos visitado ya el vecino
                if is_valid_move(neighbor) and neighbor not in visited:
                    stack.append((neighbor, path + [neighbor]))

    logger.warning(f"No se encontró un camino desde {start} hasta {goal}")
    return None
