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

    #print("path with rocks", path_with_rocks[2])
    #print("path without rocks", path_without_rocks[2])

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
    expansion_tree = {}  # Track nodes and their children

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

            # Print expansion tree
            #print("\nÁrbol de expansión:")
            #for node, children in expansion_tree.items():
            #    print(f"{node}: {children}")

            return path, visited_order, visited_by_levels

        neighbors = get_neighbors_by_priority(
            model.grid.get_neighborhood(current, moore=False, include_center=False),
            current,
            model.priority
        )

        for index, neighbor in enumerate(neighbors):
            if model.grid.out_of_bounds(neighbor):
                continue

            cell_contents = model.grid.get_cell_list_contents([neighbor])
            if any(isinstance(agent, (MetalAgent, BorderAgent)) for agent in cell_contents):
                continue
            if not allow_rocks and any(isinstance(agent, RockAgent) for agent in cell_contents):
                continue

            # Calcular el g_score temporal
            tentative_g_score = g_score[current] + 1  # Costo de movimiento

            # Si el vecino aún no tiene un g_score o se encontró un camino más corto
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                
                # Ajuste de prioridad basado en el índice del vecino
                priority_adjustment = (index + 1) * 0.0001  # Pequeño ajuste según el orden en neighbors
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal) + priority_adjustment

                # Agregar a open_set respetando el orden de `model.priority`
                heapq.heappush(open_set, (f_score[neighbor], neighbor))
                level[neighbor] = current_level + 1

                # Track expansion tree
                if current not in expansion_tree:
                    expansion_tree[current] = []
                expansion_tree[current].append(neighbor)

    # Print expansion tree if goal not reached
    #print("\nÁrbol de expansión:")
    #for node, children in expansion_tree.items():
    #    print(f"{node}: {children}")

    #return None, visited_order, visited_by_levels