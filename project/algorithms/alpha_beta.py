import math


def alpha_beta_search(state, depth, alpha, beta, maximizing_player):
    """
    Implementación del algoritmo de poda alfa-beta.
    :param state: Estado actual del juego (diccionario con grilla, posiciones, turno, etc.).
    :param depth: Profundidad máxima a explorar.
    :param alpha: Valor alfa inicial.
    :param beta: Valor beta inicial.
    :param maximizing_player: Si True, es el turno de Bomberman (maximizador); si False, del globo (minimizador).
    :return: La mejor acción (posición) y su puntaje heurístico.
    """
    if depth == 0 or is_terminal(state):
        return None, evaluate_state(state)

    if maximizing_player:
        max_eval = -math.inf
        best_action = None
        for move in get_valid_moves(state, "bomberman"):
            new_state = apply_move(state, move, "bomberman")
            _, eval = alpha_beta_search(new_state, depth - 1, alpha, beta, False)
            if eval > max_eval:
                max_eval = eval
                best_action = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return best_action, max_eval
    else:
        min_eval = math.inf
        best_action = None
        for move in get_valid_moves(state, "balloon"):
            new_state = apply_move(state, move, "balloon")
            _, eval = alpha_beta_search(new_state, depth - 1, alpha, beta, True)
            if eval < min_eval:
                min_eval = eval
                best_action = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return best_action, min_eval


def is_terminal(state):
    """
    Verifica si el estado es terminal (Bomberman llega a la meta o es capturado).
    """
    return (
        state["bomberman_pos"] == state["goal_pos"]
        or state["bomberman_pos"] == state["balloon_pos"]
    )


def evaluate_state(state):
    """
    Evalúa el estado actual para calcular una heurística.
    Menor distancia a la meta para Bomberman, mayor distancia al globo.
    """
    bomberman_to_goal = manhattan_distance(state["bomberman_pos"], state["goal_pos"])
    bomberman_to_balloon = manhattan_distance(
        state["bomberman_pos"], state["balloon_pos"]
    )
    return 10 / (bomberman_to_goal + 1) + bomberman_to_balloon  # Heurística combinada


def get_valid_moves(state, agent):
    """
    Obtiene los movimientos válidos para el agente especificado.
    """
    if agent == "bomberman":
        position = state["bomberman_pos"]
    elif agent == "balloon":
        position = state["balloon_pos"]
    else:
        raise ValueError("Agente no reconocido.")

    possible_moves = [
        (position[0] - 1, position[1]),  # Arriba
        (position[0] + 1, position[1]),  # Abajo
        (position[0], position[1] - 1),  # Izquierda
        (position[0], position[1] + 1),  # Derecha
    ]

    valid_moves = [move for move in possible_moves if is_valid_move(move, state)]
    return valid_moves


def is_valid_move(pos, state):
    """
    Verifica si una posición es válida (dentro de los límites y sin obstáculos).
    """
    x, y = pos
    grid = state["grid"]
    return (
        0 <= x < len(grid)
        and 0 <= y < len(grid[0])
        and grid[x][y] != "M"
        and grid[x][y] != "X"
    )


def apply_move(state, move, agent):
    """
    Aplica un movimiento y retorna un nuevo estado.
    """
    new_state = state.copy()
    new_state["grid"] = [row[:] for row in state["grid"]]  # Copia profunda de la grilla

    if agent == "bomberman":
        new_state["bomberman_pos"] = move
        new_state["turn"] = "balloon"
    elif agent == "balloon":
        new_state["balloon_pos"] = move
        new_state["turn"] = "bomberman"
    return new_state


def manhattan_distance(pos1, pos2):
    """
    Calcula la distancia de Manhattan entre dos posiciones.
    """
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


"""

state = {
    "grid": grid,                      # Representación del mapa (2D o lista de listas)
    "bomberman_pos": (x, y),           # Posición actual de Bomberman
    "balloon_pos": (x, y),             # Posición actual del globo
    "goal_pos": (x, y),                # Posición de la meta (G)
    "obstacles": [(x1, y1), (x2, y2)], # Lista de posiciones de obstáculos (muro 'M', borde 'X')
    "turn": "bomberman" or "balloon"   # De quién es el turno en este estado
}


-------------------------------------------------------------
state = {
    "grid": [
        ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
        ['X', 'S', 'C', 'C', 'M', 'C', 'C', 'C', 'X'],
        ['X', 'C', 'M', 'C', 'C', 'C', 'M', 'C', 'X'],
        ['X', 'C', 'C', 'M', 'M', 'C', 'M', 'G', 'X'],
        ['X', 'C', 'M', 'C', 'C', 'C', 'M', 'C', 'X'],
        ['X', 'C', 'C', 'M', 'C', 'C', 'C', 'C', 'X'],
        ['X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
    ],
    "bomberman_pos": (1, 1),  # Posición inicial de Bomberman (S)
    "balloon_pos": (5, 5),    # Ejemplo de posición inicial del globo
    "goal_pos": (3, 7),       # Meta
    "obstacles": [
        (1, 4), (2, 2), (2, 6), (3, 3), (3, 4), (3, 6),
        (4, 2), (4, 6), (5, 3)
    ],
    "turn": "bomberman"       # Turno inicial
}

"""
