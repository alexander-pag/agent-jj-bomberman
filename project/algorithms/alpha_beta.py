from config.constants import *
import random
import math


def minimax(
        model,        
        depth,
        alpha,
        beta,
        is_maximizing_player,
        current_pos_bomberman,
        current_pos_balloons,
        previous_state=None,
    ):
        # Verifica el formato de current_pos_balloons antes de pasarlo a minimax
        # print(f"Tipo de current_pos_balloons: {type(current_pos_balloons)}")
        # print(f"Contenido de current_pos_balloons: {current_pos_balloons}")

        if depth == 0 or game_over(current_pos_bomberman, current_pos_balloons):
            if is_maximizing_player:
                return (
                    heuristic_bomberman(
                        current_pos_bomberman, current_pos_balloons, model, previous_state
                    ),
                    None,
                )
            else:
                # Balloon heuristic: sum of distances to Bomberman
                return (
                    sum(
                        heuristic_balloon(current_pos_bomberman, balloon_pos)
                        for balloon_pos in current_pos_balloons
                    ),
                    None,
                )

        # Get the possible moves for Bomberman and Balloon
        bomberman_moves = get_possible_moves(
            current_pos_bomberman, is_maximizing_player
        )

        best_move = None
        if is_maximizing_player:  # Bomberman (Maximizer)
            max_eval = -math.inf
            for move in bomberman_moves:
                eval, _ = minimax(
                    depth - 1,
                    alpha,
                    beta,
                    False,
                    move,  # New position of Bomberman
                    current_pos_balloons,  # Pasar todas las posiciones de los globos
                    previous_state=(
                        current_pos_bomberman,
                        current_pos_balloons,
                    ),  # Pasar el estado anterior completo
                )
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                elif eval == max_eval:  # Si hay empate, selecciona aleatoriamente
                    best_move = random.choice([best_move, move])
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:  # Balloons (Minimizer)
            min_eval = math.inf
            best_move = (
                None  # Necesitas inicializar best_move para los globos correctamente
            )
            for balloon_idx, balloon_pos in enumerate(current_pos_balloons):
                for move in get_possible_moves(
                    balloon_pos, not is_maximizing_player, model
                ):
                    new_positions = (
                        current_pos_balloons.copy()
                    )  # Copia la lista de posiciones de los globos
                    new_positions[balloon_idx] = (
                        move  # Actualiza la posición del globo correspondiente
                    )
                    eval, _ = minimax(
                        model,
                        depth - 1,
                        alpha,
                        beta,
                        True,
                        current_pos_bomberman,
                        new_positions,  # Pasar las nuevas posiciones de los globos
                        previous_state=(
                            current_pos_bomberman,
                            current_pos_balloons,
                        ),  # Estado previo
                    )
                    if eval < min_eval:
                        min_eval = eval
                        best_move = (
                            new_positions  # Guardar el mejor conjunto de posiciones
                        )
                    elif eval == min_eval:  # Si hay empate, selecciona aleatoriamente
                        best_move = random.choice([best_move, new_positions])
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
            return (
                min_eval,
                best_move,
            )  # Aquí debes retornar el conjunto de movimientos de los globos

def heuristic_bomberman(
     current_pos_bomberman, current_pos_balloons, model, previous_state=None
):
    # Distancia a la meta
    dist_to_goal = manhattan_distance(current_pos_bomberman, model.pos_goal)

    # Calcular la distancia total a los globos
    dist_to_balloons = sum(
        manhattan_distance(current_pos_bomberman, balloon_pos)
        for balloon_pos in current_pos_balloons
    )

    # Calcular la distancia mínima a los globos
    min_dist_to_balloons = min(
        manhattan_distance(current_pos_bomberman, balloon_pos)
        for balloon_pos in current_pos_balloons
    )

    # Penalizar fuertemente si la distancia a los globos es muy baja
    balloon_penalty = 0
    if min_dist_to_balloons <= 2:  # Ajusta este umbral según necesites
        balloon_penalty = (3 - min_dist_to_balloons) * 50  # Penalización progresiva

    # Penalización adicional por repetir posiciones
    penalty = 0
    if previous_state is not None:
        if (current_pos_bomberman, tuple(current_pos_balloons)) == previous_state:
            penalty = 10

    if current_pos_bomberman in model.history:
        penalty += 20

    model.history.append(current_pos_bomberman)
    if len(model.history) > model.history_length:
        model.history.pop(0)

    # Combinar las diferentes penalizaciones y heurísticas
    return -dist_to_goal * 4 + dist_to_balloons * 5 - penalty - balloon_penalty

def heuristic_balloon( current_pos_bomberman, current_pos_balloon):
    return manhattan_distance(current_pos_balloon, current_pos_bomberman)

def get_possible_moves( current_pos, is_bomberman, model):
    # This method returns the valid neighboring positions
    neighbors = model.grid.get_neighborhood(
        current_pos, moore=False, include_center=False
    )
    valid_moves = []
    for neighbor in neighbors:
        if is_valid_move(neighbor, is_bomberman):
            valid_moves.append(neighbor)
    return valid_moves

def is_valid_move( position, is_bomberman, model):
    from agents import BombermanAgent, BorderAgent, MetalAgent, BalloonAgent
    
    # Verifica si un movimiento es válido
    cell = model.grid.get_cell_list_contents(position)

    # Prohibir moverse al borde
    if any(isinstance(agent, BorderAgent) for agent in cell):
        return False

    # Prohibir moverse a una celda con metal
    if any(isinstance(agent, MetalAgent) for agent in cell):
        return False

    # Prohibir que Bomberman se mueva a una celda ocupada por un globo
    if is_bomberman and any(isinstance(agent, BalloonAgent) for agent in cell):
        return False

    # Prohibir que los globos se muevan hacia Bomberman
    if not is_bomberman and any(
        isinstance(agent, BombermanAgent) for agent in cell
    ):
        return False

    return True

def manhattan_distance( pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def game_over( current_pos_bomberman, current_pos_balloons, model):
    # Bomberman alcanza la meta o es atrapado por un globo
    if current_pos_bomberman == model.pos_goal:
        return True
    if any(current_pos_bomberman == pos for pos in current_pos_balloons):
        return True
    return False