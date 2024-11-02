from helpers.move_by_priority import get_neighbors_by_priority
import math
from config.constants import HEURISTICS
import time


BOMB_DELAY = 1  # Tiempo de espera antes de que explote la bomba
EXPLOSION_RADIUS = 1  # Radio de explosión de la bomba


def manhattan_distance(pos1, pos2):
    """Calcula la distancia Manhattan entre dos posiciones en un grid."""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def euclidean_distance(pos1, pos2):
    """Calcula la distancia Euclidiana entre dos posiciones en un grid."""
    return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)


def get_cost(agent, current_pos) -> float:
    """
    Determina el costo de moverse a una celda en función del tipo de agente.
    """
    from agents import GrassAgent, RockAgent, MetalAgent, BorderAgent

    if isinstance(agent, (GrassAgent, RockAgent)):
        return 10
    elif isinstance(agent, (MetalAgent, BorderAgent)):
        return float("inf")
    return 1  # Costo por defecto


def place_bomb(model, bomb_position):
    """
    Coloca una bomba en la posición especificada y espera a que explote,
    destruyendo las rocas dentro de su radio de explosión.
    """

    from agents import RockAgent, GrassAgent

    print(
        f"Bomba colocada en {bomb_position}, esperando {BOMB_DELAY} segundos para explotar..."
    )
    time.sleep(BOMB_DELAY)  # Espera hasta que explote

    # Obtener posiciones dentro del radio de explosión
    neighbors = model.grid.get_neighborhood(
        bomb_position, moore=True, radius=EXPLOSION_RADIUS
    )

    # Explosión: destruye solo las rocas en el camino
    for pos in neighbors:
        cellmates = model.grid.get_cell_list_contents([pos])
        for agent in cellmates:
            if isinstance(agent, RockAgent):
                print(f"Roca destruida en {pos}")
                model.grid.remove_agent(agent)  # Remover la roca

                # Generar un ID único para el nuevo GrassAgent
                unique_id = model.next_id()  # Asegúrate de que model tenga este método
                new_grass = GrassAgent(unique_id, model)  # Reemplazar con césped
                model.grid.place_agent(new_grass, pos)
                model.schedule.add(
                    new_grass
                )  # Añadir el nuevo césped al horario de ejecución


def hill_climbing(start_pos, goal_pos, model, heuristic_type):
    from agents import RockAgent

    if heuristic_type == HEURISTICS[0]:
        heuristic = manhattan_distance
    elif heuristic_type == HEURISTICS[1]:
        heuristic = euclidean_distance
    else:
        raise ValueError("Heurística desconocida. Usa 'manhattan' o 'euclidean'.")

    current_pos = start_pos
    path = [start_pos]
    visited_order = [start_pos]

    while current_pos != goal_pos:
        neighbors = model.grid.get_neighborhood(
            current_pos, moore=False, include_center=False
        )
        ordered_neighbors = get_neighbors_by_priority(
            neighbors, current_pos, model.priority
        )

        best_neighbor = None
        best_heuristic = float("inf")

        for neighbor in ordered_neighbors:
            if neighbor not in visited_order:
                cellmates = model.grid.get_cell_list_contents([neighbor])
                move_cost = sum(get_cost(agent, current_pos) for agent in cellmates)

                # Verificar si hay una roca en el vecino
                if any(isinstance(agent, RockAgent) for agent in cellmates):
                    print(f"Roca encontrada en {neighbor}, arrojando bomba...")

                    # Coloca la bomba en la posición anterior al obstáculo
                    bomb_position = (current_pos[0] - 1, current_pos[1])
                    place_bomb(model, bomb_position)

                    # Retrocede n posiciones (a la posición antes de moverse)
                    safe_pos = path[-2] if len(path) > 1 else path[-1]
                    current_pos = safe_pos
                    visited_order.append(current_pos)
                    path.append(current_pos)  # Añade la posición de retroceso a la ruta
                    break  # Termina el ciclo para recalcular la ruta

                if move_cost < float("inf"):
                    h = heuristic(neighbor, goal_pos)
                    if h < best_heuristic:
                        best_heuristic = h
                        best_neighbor = neighbor

        if best_neighbor is None or best_heuristic >= heuristic(current_pos, goal_pos):
            found_alternative = False
            for alternative_neighbor in neighbors:
                if alternative_neighbor not in visited_order:
                    cellmates = model.grid.get_cell_list_contents(
                        [alternative_neighbor]
                    )
                    move_cost = sum(get_cost(agent, current_pos) for agent in cellmates)

                    if move_cost < float("inf"):
                        print(
                            f"Alternativa encontrada: moviendo a {alternative_neighbor}"
                        )
                        current_pos = alternative_neighbor
                        path.append(current_pos)
                        visited_order.append(current_pos)
                        found_alternative = True
                        break

            if not found_alternative:
                return None, visited_order

        else:
            print(f"Current: {current_pos}, Best: {best_neighbor}")
            current_pos = best_neighbor
            path.append(current_pos)
            visited_order.append(current_pos)

    return path, visited_order
