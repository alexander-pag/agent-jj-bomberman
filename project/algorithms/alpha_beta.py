import math
from typing import List, Tuple, Any


class StateTreeNode:
    def __init__(
        self,
        state: Any,
        depth: int,
        value: Any | None = None,
        move: Any | None = None,
        actor: Any | None = None,
        details: Any | None = None,
        children: list = None
    ):
        self.state = state
        self.depth = depth
        self.value = value
        self.move = move
        self.actor = actor
        self.details = details
        self.children = children if children is not None else []

    def __repr__(self):
        return f"StateTreeNode(depth={self.depth}, value={self.value}, state={self.state})"


def manhattan_distance(pos1, pos2):
    """Calcula la distancia Manhattan entre dos posiciones."""
    if pos1 is None or pos2 is None:
        return float("inf")
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def alpha_beta_pruning_with_tree(state, depth, alpha, beta, maximizing_player, model):
    """
    Implementa el algoritmo alpha-beta pruning con construcción de un árbol de estados.
    """
    if not isinstance(state, list) or not all(isinstance(row, list) for row in state):
        raise ValueError("El estado no tiene la estructura de una lista de listas.")

    if depth == 0 or model.is_terminal_state(state):
        value = model.evaluate_state(state, maximizing_player)
        return value, StateTreeNode(state, depth, value=value, children=[])

    node = StateTreeNode(state, depth, value=None, children=[])

    if maximizing_player:
        max_eval = float("-inf")
        possible_positions = model.get_possible_states(state, "S")  # Movimientos para Bomberman

        for new_state, new_pos in possible_positions:
            child_state = model.simulate_move(state, "S", new_pos)
            eval, child_node = alpha_beta_pruning_with_tree(
                child_state, depth - 1, alpha, beta, False, model
            )
            node.children.append(child_node)

            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break

        node.value = max_eval
        return max_eval, node

    else:
        min_eval = float("inf")
        possible_positions = model.get_possible_states(state, "B")  # Movimientos para el enemigo

        for new_state,new_pos in possible_positions:
            child_state = model.simulate_move(state, "B", new_pos)
            eval, child_node = alpha_beta_pruning_with_tree(
                child_state, depth - 1, alpha, beta, True, model
            )
            node.children.append(child_node)

            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break

        node.value = min_eval
        return min_eval, node

def get_state_details(state, model):
    """
    Obtiene detalles detallados de un estado.
    Maneja casos donde las posiciones no se encuentran.
    """
    bomberman_pos = model.find_position(state, "S")
    goal_pos = model.find_position(state, "G")
    enemy_pos = model.find_position(state, "B")

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




def move_actor(state, actor, current_pos, new_pos):
    new_state = [row[:] for row in state]  # Copiar el estado
    if current_pos:
        new_state[current_pos[1]][current_pos[0]] = "C"  # Limpia la posición actual
    new_state[new_pos[1]][new_pos[0]] = "S" if actor == "S" else "B"
    return new_state


def choose_best_move(self, model, initial_state, is_bomberman_turn):
    """
    Elige el mejor movimiento usando alfa-beta pruning.
    """
    # Determinar el actor basado en el turno
    agent = "S" if is_bomberman_turn else "B"

    # Obtener posición actual del actor
    agent_pos = model.get_agent_positions()[agent]

    # Obtener estados posibles
    possible_states = model.get_possible_states(initial_state, agent)

    print("Estados posibles generados:")
    for state, new_pos in possible_states:
        for row in state:
            print(row)
        print(f"Movimiento hacia: {new_pos}")

    # Evaluar estados
    best_move = None
    best_value = float("-inf") if is_bomberman_turn else float("inf")
    best_tree = None

    for child_state, new_pos in possible_states:
        # Evaluar el estado hijo usando poda alfa-beta
        value, state_tree = alpha_beta_pruning_with_tree(
            child_state, depth=2, alpha=float("-inf"), beta=float("inf"),
            maximizing_player=is_bomberman_turn, model=model
        )

        # Si encontramos un mejor valor, actualizamos
        if (is_bomberman_turn and value > best_value) or (not is_bomberman_turn and value < best_value):
            best_value = value
            best_move = new_pos
            best_tree = state_tree

    print("\nÁrbol de Expansión de Estados para el mejor movimiento:")
    print_state_tree(best_tree)

    # Si no hay un mejor movimiento, mantener la posición actual
    if best_move is None:
        print("No se encontró un mejor movimiento, manteniendo posición actual.")
        return agent_pos, initial_state

    # Retornar el mejor movimiento y el estado simulado
    return best_move, model.simulate_move(initial_state, agent, best_move)
