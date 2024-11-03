from collections import deque
import logging
from helpers.move_by_priority import get_neighbors_by_priority

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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

    from agents import MetalAgent, RockAgent, BorderAgent

    # Cola para almacenar el nodo actual y el camino recorrido hasta la meta
    queue = deque([(start_pos, [start_pos])])

    # Lista que mantiene el orden en que los nodos son visitados
    visited_order = []

    # Conjunto para evitar volver a visitar las mismas celdas
    visited = {start_pos}
    
    rocks_found = []  # Nueva lista para rocas

    # Obtener la prioridad seleccionada
    priority = model.priority

    while queue:
        # Extraer la posición actual y el camino hasta esa posición
        current_pos, path = queue.popleft()

        # Agregar la posición actual al orden de visita
        visited_order.append(current_pos)

        # Si llegamos a la posición objetivo, retornamos el camino y el orden de visita
        if current_pos == goal_pos:
            return path, visited_order

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
                
                # Verificar si hay roca y registrarla
                if any(isinstance(agent, RockAgent) for agent in cellmates):
                    rocks_found.append(neighbor)
                    continue
                
                if not any(
                    isinstance(agent, (MetalAgent,RockAgent, BorderAgent))
                    for agent in cellmates
                ):
                    # Agregar el vecino a la cola con el camino actualizado
                    queue.append((neighbor, path + [neighbor]))
                    visited.add(neighbor)  # Marcar el vecino como visitado

    # Si no se encontró un camino, retornamos None para el camino y el orden de visita
    logger.info(f"Rocks found during BFS: {rocks_found}")
    return None, visited_order, rocks_found
