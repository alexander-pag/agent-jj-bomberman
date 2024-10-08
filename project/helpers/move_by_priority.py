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
