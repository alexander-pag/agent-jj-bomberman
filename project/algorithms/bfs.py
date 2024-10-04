from collections import deque
from agents import MetalAgent, RockAgent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_neighbors_by_priority(neighbors, current_pos, priority):
    """
    Ordena los vecinos según la prioridad dada.

    Args:
        neighbors: Lista de vecinos.
        current_pos: Posición actual del agente.
        priority: Una cadena que indica la prioridad de exploración (ejemplo: "Arriba, Abajo, Derecha, Izquierda").

    Returns:
        Lista de vecinos ordenada según la prioridad.
    """

    print(f"LA PRIORIDAD ES: ", priority)

    # Mapeo de direcciones cardinales a coordenadas
    direction_mapping = {
        "Arriba": (current_pos[0], current_pos[1] - 1),
        "Abajo": (current_pos[0], current_pos[1] + 1),
        "Derecha": (current_pos[0] + 1, current_pos[1]),
        "Izquierda": (current_pos[0] - 1, current_pos[1]),
    }

    # Crear lista de vecinos ordenada por prioridad
    ordered_neighbors = []
    for direction in priority.split(", "):
        if direction_mapping[direction] in neighbors:
            ordered_neighbors.append(direction_mapping[direction])

    return ordered_neighbors


def bfs(start_pos, goal_pos, model):
    """
    Implementa el algoritmo de búsqueda en anchura (BFS) con prioridad de vecinos.

    Args:
        start_pos: Tupla que representa la posición inicial.
        goal_pos: Tupla que representa la posición objetivo.
        model: Modelo del entorno que contiene la información del grid y los agentes.

    Returns:
        Una tupla que contiene dos elementos:
        1. Una lista de posiciones que representa el camino encontrado, o None si no existe camino.
        2. Una lista de posiciones visitadas en el orden en que se exploraron.
    """

    # Cola para almacenar el nodo actual y el camino recorrido hasta la meta
    queue = deque([(start_pos, [start_pos])])

    # Lista que mantiene el orden en que los nodos son visitados
    visited_order = []

    # Conjunto para evitar volver a visitar las mismas celdas
    visited = set()

    # Obtener la prioridad seleccionada
    priority = model.priority

    while queue:
        logger.info(f"Lista de nodos visitados: {visited}")
        logger.info(f"Cola de nodos: {queue}")

        # Extraer la posición actual y el camino hasta esa posición
        current_pos, path = queue.popleft()

        # Agregar la posición actual al orden de visita
        visited_order.append(current_pos)

        # Si llegamos a la posición objetivo, retornamos el camino y el orden de visita
        if current_pos == goal_pos:
            return path, visited_order

        # Marcar la celda actual como visitada
        visited.add(current_pos)

        # Obtener las celdas vecinas ortogonalmente (sin diagonales, sin incluir el centro)
        neighbors = model.grid.get_neighborhood(
            current_pos, moore=False, include_center=False
        )

        # Ordenar los vecinos según la prioridad seleccionada
        neighbors = get_neighbors_by_priority(neighbors, current_pos, priority)

        for neighbor in neighbors:
            # Si el vecino no ha sido visitado antes
            if neighbor not in visited:
                # Verificar que la celda no esté ocupada por obstáculos
                cellmates = model.grid.get_cell_list_contents([neighbor])
                if not any(
                    isinstance(agent, (MetalAgent, RockAgent)) for agent in cellmates
                ):
                    # Agregar el vecino a la cola con el camino actualizado
                    queue.append((neighbor, path + [neighbor]))
                    visited.add(neighbor)  # Marcar el vecino como visitado

    # Si no se encontró un camino, retornamos None para el camino y el orden de visita
    logger.warning(f"No se encontró un camino desde {start_pos} hasta {goal_pos}")
    return None, visited_order
