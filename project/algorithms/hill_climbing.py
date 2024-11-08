from helpers.move_by_priority import get_neighbors_by_priority
import math
from config.constants import HEURISTICS
from helpers.calculate_path import *


def hill_climbing(start_pos, goal_pos, model, heuristic_type):
    """Hill climbing comparing paths with and without rocks."""
    # Find both paths
    path_with_rocks = find_path(
        start_pos, goal_pos, model, heuristic_type, allow_rocks=True
    )
    path_without_rocks = find_path(
        start_pos, goal_pos, model, heuristic_type, allow_rocks=False
    )

    # Calculate costs
    rocks_in_path = []
    if path_with_rocks[0]:
        rocks_in_path = path_with_rocks[2]

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
    
    print("Cantidad de retrocesos: ", path_with_rocks[4])
    
    print("Nodos expandidos por niveles:")
    for lvl, nodes in path_with_rocks[3].items():
        print(f"Nivel {lvl}: {nodes}")

    # Return optimal path
    if cost_with_rocks < cost_without_rocks:
        return path_with_rocks[0], path_with_rocks[1], rocks_in_path
    return path_without_rocks[0], path_without_rocks[1], []


def find_path(start_pos, goal_pos, model, heuristic_type, allow_rocks=False):
    """Find path using hill climbing."""
    from agents import RockAgent, MetalAgent, BorderAgent

    if heuristic_type == HEURISTICS[0]:
        heuristic = manhattan_distance
    elif heuristic_type == HEURISTICS[1]:
        heuristic = euclidean_distance
    else:
        raise ValueError("Heurística desconocida. Usa 'manhattan' o 'euclidean'.")

    current_pos = start_pos
    path = [start_pos]
    visited_order = [start_pos]
    rocks_found = []
    visited_by_levels = {}
    nodes_with_unexplored = {}
    level = 0
    max_level = 0  # Mantiene el nivel máximo alcanzado en cualquier punto
    cantRetrocesos = 0

    visited_by_levels[level] = [current_pos]

    def get_valid_neighbors(pos):
        """Helper function to get valid unvisited neighbors."""
        neighbors = model.grid.get_neighborhood(pos, moore=False, include_center=False)
        ordered_neighbors = get_neighbors_by_priority(neighbors, pos, model.priority)
        valid = []
        for n in ordered_neighbors:
            if n not in visited_order:
                cellmates = model.grid.get_cell_list_contents([n])
                if any(isinstance(agent, RockAgent) for agent in cellmates):
                    if n not in rocks_found:
                        rocks_found.append(n)
                    if not allow_rocks:
                        continue
                if any(isinstance(agent, MetalAgent) for agent in cellmates) or \
                   any(isinstance(agent, BorderAgent) for agent in cellmates):
                    continue
                valid.append(n)
        return valid

    def update_unexplored_nodes():
        """Update the list of unexplored neighbors for all recorded nodes."""
        nodes_to_remove = []
        for node_pos in list(nodes_with_unexplored.keys()):
            valid_neighbors = get_valid_neighbors(node_pos)
            if valid_neighbors:
                valid_neighbors = [n for n in valid_neighbors if n not in path]
                if valid_neighbors:
                    nodes_with_unexplored[node_pos]['neighbors'] = valid_neighbors
                else:
                    nodes_to_remove.append(node_pos)
            else:
                nodes_to_remove.append(node_pos)
        
        for node_pos in nodes_to_remove:
            if node_pos in nodes_with_unexplored:
                del nodes_with_unexplored[node_pos]

    while current_pos != goal_pos:
        valid_neighbors = get_valid_neighbors(current_pos)

        if valid_neighbors:
            nodes_with_unexplored[current_pos] = {
                'level': level,
                'neighbors': valid_neighbors.copy(),
                'path_to_here': path.copy()
            }
            print(f"\nEn nodo {current_pos} nivel {level}")
            print(f"Vecinos válidos: {valid_neighbors}")

            best_neighbor = min(valid_neighbors, key=lambda n: heuristic(n, goal_pos))
            current_pos = best_neighbor
            path.append(current_pos)
            visited_order.append(current_pos)

            level += 1
            max_level = max(max_level, level)  # Actualiza el nivel máximo alcanzado

            if level not in visited_by_levels:
                visited_by_levels[level] = []
            visited_by_levels[level].append(current_pos)

            update_unexplored_nodes()

        else:
            print(f"\nCallejón sin salida en nodo {current_pos}")
            print("Nodos con caminos sin explorar:")
            for pos, data in nodes_with_unexplored.items():
                print(f"Nodo {pos} (nivel {data['level']}): {data['neighbors']}")

            valid_backtrack_nodes = {}
            for pos, data in nodes_with_unexplored.items():
                valid_neighbors = get_valid_neighbors(pos)
                if valid_neighbors:
                    valid_backtrack_nodes[pos] = data

            if not valid_backtrack_nodes:
                return None, visited_order, rocks_found, visited_by_levels, cantRetrocesos

            lowest_level_node = min(valid_backtrack_nodes.items(), 
                                  key=lambda x: x[1]['level'])
            backtrack_pos = lowest_level_node[0]
            print(f"Retrocediendo al nodo {backtrack_pos} en nivel {lowest_level_node[1]['level']}")
            cantRetrocesos += 1

            path = nodes_with_unexplored[backtrack_pos]['path_to_here'].copy()
            
            level = max_level  # Establece el nivel como el último nivel máximo alcanzado

            valid_neighbors = get_valid_neighbors(backtrack_pos)
            if not valid_neighbors:
                del nodes_with_unexplored[backtrack_pos]
                continue

            next_neighbor = min(valid_neighbors, key=lambda n: heuristic(n, goal_pos))
            if not nodes_with_unexplored[backtrack_pos]['neighbors']:
                del nodes_with_unexplored[backtrack_pos]

            current_pos = next_neighbor
            path.append(current_pos)
            visited_order.append(current_pos)
            level += 1  # Incrementa el nivel desde el nivel máximo

            update_unexplored_nodes()

    return path, visited_order, rocks_found, visited_by_levels, cantRetrocesos

