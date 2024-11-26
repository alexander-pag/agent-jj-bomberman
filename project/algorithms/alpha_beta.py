import math
from typing import List, Tuple, Any


class StateTreeNode:
    def __init__(self, state, depth, value=None, move=None, actor=None, details=None):
        self.state = state
        self.depth = depth
        self.value = value
        self.move = move
        self.actor = actor
        self.details = details or {}
        self.children = []


def manhattan_distance(pos1, pos2):
    """Calcula la distancia Manhattan entre dos posiciones."""
    if pos1 is None or pos2 is None:
        return float("inf")
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def alpha_beta_pruning_with_tree(
    state,
    depth,
    alpha,
    beta,
    maximizing_player,
    model,
    max_depth=2,
    current_move=None,
    actor=None,
):
    """
    Implementación del algoritmo de poda alfa-beta para Bomberman con construcción de árbol.
    """
    # Condiciones de parada
    if depth == 0 or is_terminal_state(state, model):
        value = evaluate_state(state, maximizing_player, model)
        details = get_state_details(state, model)
        return value, StateTreeNode(
            state, depth, value=value, move=current_move, actor=actor, details=details
        )

    node = StateTreeNode(state, depth, move=current_move, actor=actor)

    if maximizing_player:  # Turno de Bomberman
        max_eval = float("-inf")
        possible_states = get_possible_states(state, find_position(state, "S"), model)

        if not possible_states:
            return float("-inf"), node

        for child_pos in possible_states:
            # Crear nuevo estado moviendo a Bomberman
            child_state = move_actor(state, "S", find_position(state, "S"), child_pos)

            # Recursión con minimizando el siguiente nivel (turno del enemigo)
            eval, child_node = alpha_beta_pruning_with_tree(
                child_state,
                depth - 1,
                alpha,
                beta,
                False,
                model,
                max_depth,
                current_move=child_pos,
                actor="S",
            )

            node.children.append(child_node)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)

            # Condiciones de poda
            if beta <= alpha or depth == max_depth:
                break
        return max_eval, node

    else:  # Turno del globo (minimizando)
        min_eval = float("inf")
        possible_states = get_possible_states(state, find_position(state, "E"), model)

        if not possible_states:
            return float("inf"), node

        for child_pos in possible_states:
            # Crear nuevo estado moviendo al enemigo
            child_state = move_actor(state, "E", find_position(state, "E"), child_pos)

            # Recursión con maximizando el siguiente nivel (turno de Bomberman)
            eval, child_node = alpha_beta_pruning_with_tree(
                child_state,
                depth - 1,
                alpha,
                beta,
                True,
                model,
                max_depth,
                current_move=child_pos,
                actor="E",
            )

            node.children.append(child_node)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)

            # Condiciones de poda
            if beta <= alpha or depth == max_depth:
                break
        return min_eval, node


def get_state_details(state, model):
    """
    Obtiene detalles detallados de un estado.
    Maneja casos donde las posiciones no se encuentran.
    """
    bomberman_pos = find_position(state, "S")
    goal_pos = find_position(state, "G")
    enemy_pos = find_position(state, "E")

    # Si alguna posición no se encuentra, devolver detalles con valores por defecto
    if bomberman_pos is None or goal_pos is None or enemy_pos is None:
        return {
            "bomberman_pos": None,
            "goal_pos": None,
            "enemy_pos": None,
            "distance_to_goal": float("inf"),
            "distance_to_enemy": float("inf"),
        }

    return {
        "bomberman_pos": bomberman_pos,
        "goal_pos": goal_pos,
        "enemy_pos": enemy_pos,
        "distance_to_goal": manhattan_distance(bomberman_pos, goal_pos),
        "distance_to_enemy": manhattan_distance(bomberman_pos, enemy_pos),
    }


def print_state_tree(node, indent=""):
    """
    Imprime el árbol de estados de forma recursiva con detalles.
    """
    move_info = f"Move: {node.move}" if node.move else "Initial State"
    actor_info = f"Actor: {node.actor}" if node.actor else ""
    value_info = f"Value: {node.value:.2f}" if node.value is not None else ""

    print(f"{indent}└── {move_info} {actor_info} {value_info}")

    # Imprimir detalles si existen
    if node.details:
        details = node.details
        print(f"{indent}    Bomberman Position: {details.get('bomberman_pos')}")
        print(f"{indent}    Goal Position: {details.get('goal_pos')}")
        print(f"{indent}    Enemy Position: {details.get('enemy_pos')}")
        print(f"{indent}    Distance to Goal: {details.get('distance_to_goal')}")
        print(f"{indent}    Distance to Enemy: {details.get('distance_to_enemy')}")

    for child in node.children:
        print_state_tree(child, indent + "    ")


def evaluate_state(state, maximizing_player, model):
    """
    Evalúa el estado actual del juego con una heurística multifactorial.
    """
    bomberman_pos = find_position(state, "S")
    goal_pos = find_position(state, "G")
    enemy_pos = find_position(state, "E")

    # Casos terminales con mayor prioridad
    if not bomberman_pos or not goal_pos or not enemy_pos:
        return 0  # Estado no válido

    if bomberman_pos == goal_pos:
        return float("inf")  # Victoria de Bomberman

    if bomberman_pos == enemy_pos:
        return float("-inf")  # Derrota de Bomberman

    # Heurística multiobjetivo
    distance_to_goal = manhattan_distance(bomberman_pos, goal_pos)
    distance_to_enemy = manhattan_distance(bomberman_pos, enemy_pos)

    if maximizing_player:  # Turno de Bomberman
        # Prioriza acercarse a la meta y alejarse del enemigo
        score = -distance_to_goal * 2 + distance_to_enemy
    else:  # Turno del globo
        # Prioriza acercarse a Bomberman
        score = distance_to_enemy

    return score


def find_position(state, actor):
    for y, row in enumerate(state):
        for x, cell in enumerate(row):
            if cell == actor:
                return (x, y)
    print(f"Actor {actor} no encontrado en el estado.")
    return None


def get_possible_states(state, current_pos, model):
    print(f"Debug - Current Position: {current_pos}")
    neighbors = model.grid.get_neighborhood(
        current_pos, moore=False, include_center=False
    )

    valid_states = []
    for neighbor in neighbors:
        if is_valid_move(neighbor, model):
            valid_states.append(neighbor)

    return valid_states


def is_valid_move(position, model):
    x, y = position

    # Verificar límites del mapa
    if x < 0 or x >= model.width or y < 0 or y >= model.height:
        return False

    cell_contents = model.grid.get_cell_list_contents(position)
    from agents import MetalAgent, BorderAgent

    # Verificar obstáculos
    for agent in cell_contents:
        if isinstance(agent, (MetalAgent, BorderAgent)):
            return False

    return True


def move_actor(state, actor, current_pos, new_pos):
    new_state = [row[:] for row in state]  # Copiar el estado
    if current_pos:
        new_state[current_pos[1]][current_pos[0]] = "C"  # Limpia la posición actual
    new_state[new_pos[1]][new_pos[0]] = "S" if actor == "S" else "E"
    return new_state


def choose_best_move(model, initial_state, is_bomberman_turn):
    """
    Elige el mejor movimiento usando alfa-beta pruning.
    """
    bomberman_pos = model.get_agent_positions()["Bomberman"]
    print(f"Debug - Bomberman Position: {bomberman_pos}")
    print(f"Debug - Initial State: {initial_state}")

    best_move = None
    best_value = float("-inf") if is_bomberman_turn else float("inf")
    best_tree = None

    possible_states = get_possible_states(initial_state, bomberman_pos, model)

    print("Evaluando movimientos posibles de Bomberman:")
    for child_pos in possible_states:
        # Create a new state by moving Bomberman
        child_state = move_actor(initial_state, "S", bomberman_pos, child_pos)

        value, state_tree = alpha_beta_pruning_with_tree(
            child_state,
            depth=2,  # Aumenté la profundidad para más detalle
            alpha=float("-inf"),
            beta=float("inf"),
            maximizing_player=is_bomberman_turn,
            model=model,
        )

        print(f"\nMovimiento a {child_pos}:")
        print(f"Valor de evaluación: {value}")

        if is_bomberman_turn and value > best_value:
            best_value = value
            best_move = child_pos
            best_tree = state_tree
        elif not is_bomberman_turn and value < best_value:
            best_value = value
            best_move = child_pos
            best_tree = state_tree

    print("\nÁrbol de Expansión de Estados para el mejor movimiento:")
    print_state_tree(best_tree)

    return best_move if best_move else bomberman_pos


def is_terminal_state(state, model):
    bomberman_pos = find_position(state, "S")
    goal_pos = find_position(state, "G")
    enemy_pos = find_position(state, "E")
    return bomberman_pos == goal_pos or bomberman_pos == enemy_pos
