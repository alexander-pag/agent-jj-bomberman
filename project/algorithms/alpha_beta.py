import math
<<<<<<< HEAD
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
        return float('inf')
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def alpha_beta_pruning_with_tree(state, depth, alpha, beta, maximizing_player, model, max_depth=2, current_move=None, actor=None):
    """
    Implementación del algoritmo de poda alfa-beta para Bomberman con construcción de árbol.
    """
    # Condiciones de parada
    if depth == 0 or is_terminal_state(state, model):
        value = evaluate_state(state, maximizing_player, model)
        details = get_state_details(state, model)
        return value, StateTreeNode(state, depth, value=value, move=current_move, actor=actor, details=details)

    node = StateTreeNode(state, depth, move=current_move, actor=actor)
    
    if maximizing_player:  # Turno de Bomberman
        max_eval = float('-inf')
        possible_states = get_possible_states(state, find_position(state, "Bomberman"), model)
        
        if not possible_states:
            return float('-inf'), node
        
        for child_pos in possible_states:
            # Crear nuevo estado moviendo a Bomberman
            child_state = move_actor(state, "Bomberman", find_position(state, "Bomberman"), child_pos)
            
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
                actor="Bomberman"
            )
            
            node.children.append(child_node)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            
            # Condiciones de poda
            if beta <= alpha or depth == max_depth:
                break
        return max_eval, node
    
    else:  # Turno del globo (minimizando)
        min_eval = float('inf')
        possible_states = get_possible_states(state, find_position(state, "Enemy"), model)
        
        if not possible_states:
            return float('inf'), node
        
        for child_pos in possible_states:
            # Crear nuevo estado moviendo al enemigo
            child_state = move_actor(state, "Enemy", find_position(state, "Enemy"), child_pos)
            
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
                actor="Enemy"
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
    bomberman_pos = find_position(state, "Bomberman")
    goal_pos = find_position(state, "G")
    enemy_pos = find_position(state, "Enemy")
    
    # Si alguna posición no se encuentra, devolver detalles con valores por defecto
    if bomberman_pos is None or goal_pos is None or enemy_pos is None:
        return {
            "bomberman_pos": None,
            "goal_pos": None,
            "enemy_pos": None,
            "distance_to_goal": float('inf'),
            "distance_to_enemy": float('inf')
        }
    
    return {
        "bomberman_pos": bomberman_pos,
        "goal_pos": goal_pos,
        "enemy_pos": enemy_pos,
        "distance_to_goal": manhattan_distance(bomberman_pos, goal_pos),
        "distance_to_enemy": manhattan_distance(bomberman_pos, enemy_pos)
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
    bomberman_pos = find_position(state, "Bomberman")
    goal_pos = find_position(state, "G")
    enemy_pos = find_position(state, "Enemy")

    # Casos terminales con mayor prioridad
    if not bomberman_pos or not goal_pos or not enemy_pos:
        return 0  # Estado no válido

    if bomberman_pos == goal_pos:
        return float('inf')  # Victoria de Bomberman
    
    if bomberman_pos == enemy_pos:
        return float('-inf')  # Derrota de Bomberman

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
    neighbors = model.grid.get_neighborhood(current_pos, moore=False, include_center=False)
    
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
    new_state[new_pos[1]][new_pos[0]] = "Bomberman" if actor == "Bomberman" else "Enemy"
    return new_state


def choose_best_move(model, initial_state, is_bomberman_turn):
    """
    Elige el mejor movimiento usando alfa-beta pruning.
    """
    bomberman_pos = model.get_agent_positions()['Bomberman']
    print(f"Debug - Bomberman Position: {bomberman_pos}")
    print(f"Debug - Initial State: {initial_state}")
    
    best_move = None
    best_value = float('-inf') if is_bomberman_turn else float('inf')
    best_tree = None
    
    possible_states = get_possible_states(initial_state, bomberman_pos, model)
    
    print("Evaluando movimientos posibles de Bomberman:")
    for child_pos in possible_states:
        # Create a new state by moving Bomberman
        child_state = move_actor(initial_state, "Bomberman", bomberman_pos, child_pos)
        
        value, state_tree = alpha_beta_pruning_with_tree(
            child_state, 
            depth=2,  # Aumenté la profundidad para más detalle 
            alpha=float('-inf'), 
            beta=float('inf'), 
            maximizing_player=is_bomberman_turn, 
            model=model
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
    bomberman_pos = find_position(state, "Bomberman")
    goal_pos = find_position(state, "G")
    enemy_pos = find_position(state, "Enemy")
    return bomberman_pos == goal_pos or bomberman_pos == enemy_pos
=======


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
>>>>>>> 28c28a4239c5b15cb236fd04ca167ac034f88bab
