import logging
from helpers.move_by_priority import get_neighbors_by_priority

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

    from agents import RockAgent, MetalAgent, BorderAgent

    def is_valid_move(pos, rocks) -> bool:
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
            if isinstance(agent, (MetalAgent, BorderAgent)):
                return False
            if isinstance(agent, RockAgent):
                # sin rocas repetidas
                if agent.pos not in rocks:
                    rocks.append(agent.pos)
        return True

    # Pila para el recorrido DFS (almacena los nodos a visitar y el camino recorrido hasta ahora)
    stack = [(start, [start])]

    # Conjunto para almacenar las celdas visitadas
    visited = set()

    # Lista que mantiene el orden en que los nodos son visitados
    visited_order = []

    # Prioridad de exploración
    priority = model.priority

    rocks_found = []  # Nueva lista para rocas

    while stack:
        current, path = stack.pop()

        visited_order.append(current)

        # Si hemos alcanzado el objetivo, devolvemos el camino
        if current == goal:
            return path, visited_order, rocks_found

        if current not in visited:
            visited.add(current)

            # Obtener los vecinos válidos
            neighbors = model.grid.get_neighborhood(
                current, moore=False, include_center=False
            )

            # Ordenar los vecinos según la prioridad
            ordered_neighbors = get_neighbors_by_priority(neighbors, current, priority)

            # Invertir el orden de los vecinos antes de añadirlos a la pila
            # para asegurarnos de que el vecino de mayor prioridad se explore primero
            for neighbor in reversed(ordered_neighbors):
                # Verificar si el movimiento es válido y si no hemos visitado ya el vecino
                if is_valid_move(neighbor, rocks_found) and neighbor not in visited:
                    stack.append((neighbor, path + [neighbor]))

    return None, visited_order
