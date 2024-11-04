from helpers.move_by_priority import get_neighbors_by_priority
import math
from config.constants import HEURISTICS


def manhattan_distance(pos1, pos2):
    """Calcula la distancia Manhattan entre dos posiciones en un grid."""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def euclidean_distance(pos1, pos2):
    """Calcula la distancia Euclidiana entre dos posiciones en un grid."""
    return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)


def hill_climbing(start_pos, goal_pos, model, heuristic_type):
    from agents import RockAgent, MetalAgent

    # Selección de la heurística
    if heuristic_type == HEURISTICS[0]:
        heuristic = manhattan_distance
    elif heuristic_type == HEURISTICS[1]:
        heuristic = euclidean_distance
    else:
        raise ValueError("Heurística desconocida. Usa 'manhattan' o 'euclidean'.")

    current_pos = start_pos
    path = [start_pos]
    visited_order = [start_pos]
    rocks_found = []  # Lista para almacenar posiciones de rocas encontradas

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

                # Registrar la posición de rocas, pero no bloquear el movimiento
                if any(isinstance(agent, RockAgent) for agent in cellmates):
                    rocks_found.append(neighbor)

                # Bloquear el movimiento a celdas con metales
                if any(isinstance(agent, MetalAgent) for agent in cellmates):
                    continue  # Omite vecinos que contengan metales

                # Calcular la heurística para el vecino válido
                h = heuristic(neighbor, goal_pos)
                if h < best_heuristic:
                    best_heuristic = h
                    best_neighbor = neighbor

        if best_neighbor is None or best_heuristic >= heuristic(current_pos, goal_pos):
            # No hay camino directo; retroceder y recalcular
            found_alternative = False
            while path and not found_alternative:
                # Retrocede al paso anterior
                path.pop()
                if path:
                    current_pos = path[-1]
                    visited_order.append(current_pos)

                    # Intenta encontrar un nuevo vecino sin metal
                    neighbors = model.grid.get_neighborhood(
                        current_pos, moore=False, include_center=False
                    )
                    for alternative_neighbor in neighbors:
                        if alternative_neighbor not in visited_order:
                            cellmates = model.grid.get_cell_list_contents(
                                [alternative_neighbor]
                            )
                            if all(
                                not isinstance(agent, MetalAgent) for agent in cellmates
                            ):
                                # Si el vecino es válido, continúa desde aquí
                                current_pos = alternative_neighbor
                                path.append(current_pos)
                                visited_order.append(current_pos)
                                found_alternative = True
                                break

            if not found_alternative:
                return (
                    None,
                    visited_order,
                    rocks_found,
                )  # No se encontró una ruta alternativa

        else:
            # Avanzar al mejor vecino encontrado
            current_pos = best_neighbor
            path.append(current_pos)
            visited_order.append(current_pos)

    return path, visited_order, rocks_found
