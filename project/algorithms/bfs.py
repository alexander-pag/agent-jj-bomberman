from collections import deque
from agents import MetalAgent, RockAgent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def bfs(start_pos, goal_pos, model) -> list:
    """
    Implementa el algoritmo de búsqueda en anchura (BFS) para encontrar un camino
    desde una posición inicial hasta una posición objetivo en un modelo de grid.

    Args:
        start_pos: Tupla que representa la posición inicial.
        goal_pos: Tupla que representa la posición objetivo.
        model: Modelo del entorno que contiene la información del grid y los agentes.

    Returns:
        Una lista de posiciones que representa el camino encontrado, o None si no existe camino.
    """

    # Cola para almacenar el nodo actual y el camino recorrido hasta la meta
    queue = deque([(start_pos, [start_pos])])
    # Inicializamos una cola con el nodo inicial y el camino que lleva hasta él (solo el inicio)

    visited = set()  # Conjunto de nodos visitados
    # Creamos un conjunto para llevar un registro de las celdas que ya hemos explorado

    # Mientras la cola no esté vacía, seguimos buscando
    while queue:

        logger.info(f"Lista de nodos visitados: {visited}")
        logger.info(f"Cola de nodos: {queue}")

        current_pos, path = queue.popleft()
        # Sacamos el primer elemento de la cola: la posición actual y el camino hasta ella

        # Si ya alcanzamos la meta, retornamos el camino
        if current_pos == goal_pos:
            return path

        # Marcar la celda actual como visitada
        visited.add(current_pos)

        # Obtener las celdas vecinas ortogonalmente
        neighbors = model.grid.get_neighborhood(
            current_pos, moore=False, include_center=False
        )
        # Obtenemos las celdas vecinas a la posición actual (sin diagonales y sin incluir la celda misma)

        for neighbor in neighbors:
            # Iteramos sobre cada vecino

            if neighbor not in visited:
                # Si el vecino no ha sido visitado antes

                # Verificar que la celda no esté ocupada por obstáculos
                cellmates = model.grid.get_cell_list_contents([neighbor])
                if not any(
                    isinstance(agent, (MetalAgent, RockAgent)) for agent in cellmates
                ):
                    # Si la celda no está ocupada por rocas o metales
                    queue.append((neighbor, path + [neighbor]))
                    # Agregamos el vecino a la cola con el camino actualizado
                    visited.add(neighbor)

    logger.warning(f"No se encontró un camino desde {start_pos} hasta {goal_pos}")
    return None
