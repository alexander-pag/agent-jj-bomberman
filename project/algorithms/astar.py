import heapq
from config.constants import HEURISTICS
from helpers.move_by_priority import get_neighbors_by_priority
from collections import Counter
from helpers.calculate_path import *

costos = []

def astar_search(start, goal, model, heuristic_type) -> tuple:
    """A* search comparing paths with and without rocks."""
    from agents import RockAgent

    global costos

    # Find both paths
    path_with_rocks = find_path(start, goal, model, heuristic_type, costos, allow_rocks=True)
    path_without_rocks = find_path(start, goal, model, heuristic_type, costos, allow_rocks=False)

    # Eliminar las celdas repetidas
    costos = list(set(costos))

    # Contar las frecuencias de cada función de costo
    cost_frequencies = Counter([costo[1] for costo in costos])

    # Obtener los costos más y menos repetidos
    most_repeated_cost = max(cost_frequencies, key=cost_frequencies.get)
    least_repeated_cost = min(cost_frequencies, key=cost_frequencies.get)

    # Obtener las celdas asociadas a cada costo
    celdas_most = [costo[0] for costo in costos if costo[1] == most_repeated_cost]
    celdas_least = [costo[0] for costo in costos if costo[1] == least_repeated_cost]

    print(f"La función de costo más repetida es: {most_repeated_cost}")
    print(f"Las celdas con la función de costo más repetida son: {celdas_most}")
    print(f"La función de costo menos repetida es: {least_repeated_cost}")
    print(f"Las celdas con la función de costo menos repetida son: {celdas_least}")

    print("path with rocks", path_with_rocks[2])
    print("path without rocks", path_without_rocks[2])

    # Calculate costs
    rocks_in_path = []
    if path_with_rocks[0]:
        rocks_in_path = [
            pos
            for pos in path_with_rocks[0]
            if any(
                isinstance(agent, RockAgent)
                for agent in model.grid.get_cell_list_contents([pos])
            )
        ]

    cost_with_rocks = calculate_path_cost(path_with_rocks[0], rocks_in_path)
    cost_without_rocks = calculate_path_cost(path_without_rocks[0], [])

    print("\nComparación de costos:")
    print(
        f"Camino con rocas: {cost_with_rocks} pasos (básico: {len(path_with_rocks[0]) if path_with_rocks[0] else 'inf'}, rocas: {len(rocks_in_path)})"
    )
    print(f"Camino sin rocas: {cost_without_rocks} pasos")
    print(
        f"Eligiendo camino {'con' if cost_with_rocks < cost_without_rocks else 'sin'} rocas\n"
    )

    # Return optimal path
    if cost_with_rocks < cost_without_rocks:
        return path_with_rocks[0], path_with_rocks[1], rocks_in_path
    return path_without_rocks[0], path_without_rocks[1], []

def find_path(start, goal, model, heuristic_type, costos, allow_rocks=False):
    """Helper function to find path with A*."""
    from agents import RockAgent, MetalAgent, BorderAgent

    if heuristic_type == HEURISTICS[0]:
        heuristic = manhattan_distance
    elif heuristic_type == HEURISTICS[1]:
        heuristic = euclidean_distance
    else:
        raise ValueError("Heurística desconocida. Usa 'manhattan' o 'euclidean'.")

    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    visited_order = []
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}
    visited_by_levels = {}
    level = {start: 0}

    while open_set:
        _, current = heapq.heappop(open_set)
        visited_order.append(current)

        current_level = level[current]
        if current_level not in visited_by_levels:
            visited_by_levels[current_level] = []
        visited_by_levels[current_level].append(current)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()

            return path, visited_order, visited_by_levels

        neighbors = get_neighbors_by_priority(
            model.grid.get_neighborhood(current, moore=False, include_center=False),
            current,
            model.priority
        )

        for neighbor in neighbors:
            if model.grid.out_of_bounds(neighbor):
                continue

            cell_contents = model.grid.get_cell_list_contents([neighbor])
            if any(
                isinstance(agent, (MetalAgent, BorderAgent)) for agent in cell_contents
            ):
                continue

            if not allow_rocks and any(
                isinstance(agent, RockAgent) for agent in cell_contents
            ):
                continue

            tentative_g_score = g_score[current] + 1  # Costo de 1 por cada paso
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)

                costos.append((neighbor, f_score[neighbor]))

                heapq.heappush(open_set, (f_score[neighbor], neighbor))
                level[neighbor] = current_level + 1

    return None, visited_order, visited_by_levels