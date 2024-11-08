from helpers.move_by_priority import get_neighbors_by_priority
import math
from config.constants import HEURISTICS
from helpers.calculate_path import *


def beam_search(start_pos, goal_pos, model, heuristic_type, beam_width=2):
    """Beam search comparing paths with and without rocks."""
    # Find both paths
    path_with_rocks = find_path(
        start_pos,
        goal_pos,
        model,
        heuristic_type,
        allow_rocks=True,
        beam_width=beam_width,
    )
    path_without_rocks = find_path(
        start_pos,
        goal_pos,
        model,
        heuristic_type,
        allow_rocks=False,
        beam_width=beam_width,
    )

    # Handle cases where no path is found
    if not path_with_rocks:
        print("No se encontró un camino con rocas.")
        path_with_rocks = ([], [], [])
    if not path_without_rocks:
        print("No se encontró un camino sin rocas.")
        path_without_rocks = ([], [], [])

    # Calculate costs
    rocks_in_path = path_with_rocks[2] if path_with_rocks[0] else []
    cost_with_rocks = (
        calculate_path_cost(path_with_rocks[0], rocks_in_path)
        if path_with_rocks[0]
        else float("inf")
    )
    cost_without_rocks = (
        calculate_path_cost(path_without_rocks[0], [])
        if path_without_rocks[0]
        else float("inf")
    )

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


def find_path(
    start_pos, goal_pos, model, heuristic_type, allow_rocks=False, beam_width=2
):
    from agents import RockAgent, MetalAgent, BorderAgent

    if heuristic_type == HEURISTICS[0]:
        heuristic = manhattan_distance
    elif heuristic_type == HEURISTICS[1]:
        heuristic = euclidean_distance
    else:
        raise ValueError("Heurística desconocida. Usa 'manhattan' o 'euclidean'.")

    current_nodes = [(start_pos, [start_pos])]
    visited_order = []  # Mantendremos solo los nodos realmente expandidos aquí
    rocks_found = []
    visited_by_levels = {}
    level = 0
    cantRetrocesos = 0

    # Guarda solo los nodos de expansión
    expanded_nodes_in_path = set()  # Nodos realmente expandidos en el camino
    visited_by_levels[level] = [start_pos]

    def get_valid_neighbors(pos):
        neighbors = model.grid.get_neighborhood(pos, moore=False, include_center=False)
        ordered_neighbors = get_neighbors_by_priority(neighbors, pos, model.priority)
        valid = []
        for n in ordered_neighbors:
            if n not in expanded_nodes_in_path:  # Ahora revisamos los nodos expandidos
                cellmates = model.grid.get_cell_list_contents([n])
                if any(isinstance(agent, RockAgent) for agent in cellmates):
                    if n not in rocks_found:
                        rocks_found.append(n)
                    if not allow_rocks:
                        continue
                if any(isinstance(agent, MetalAgent) for agent in cellmates) or any(
                    isinstance(agent, BorderAgent) for agent in cellmates
                ):
                    continue
                valid.append(n)
        return valid

    while current_nodes:
        next_nodes = []
        expanded_nodes = [pos for pos, _ in current_nodes if pos not in expanded_nodes_in_path]
        
        # Registra solo nodos de expansión en el nivel actual
        if expanded_nodes:
            visited_by_levels[level] = expanded_nodes
            expanded_nodes_in_path.update(expanded_nodes)
            visited_order.extend(expanded_nodes)  # Agrega los nodos de expansión al orden de visita

        for current_pos, path in current_nodes:
            if current_pos == goal_pos:
                return (
                    path,
                    visited_order,  # Esto ahora solo contiene nodos expandidos
                    rocks_found,
                    visited_by_levels,
                    cantRetrocesos,
                )

            valid_neighbors = get_valid_neighbors(current_pos)

            if valid_neighbors:
                for neighbor in valid_neighbors:
                    new_path = path + [neighbor]
                    next_nodes.append((neighbor, new_path))
            else:
                print(f"camino sin salida en {current_pos}")
                cantRetrocesos += 1  # Incrementa el contador de retrocesos

        # Ordenar y seleccionar el ancho de haz
        next_nodes.sort(key=lambda x: heuristic(x[0], goal_pos))
        current_nodes = next_nodes[:beam_width]
        level += 1

    return None  # Si no se encuentra un camino
