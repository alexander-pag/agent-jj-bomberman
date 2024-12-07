from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agents import (
    BombermanAgent,
    GrassAgent,
    MetalAgent,
    RockAgent,
    BorderAgent,
    GoalAgent,
    BalloonAgent,
)
from config.constants import *
import random
import math
from helpers.tree_visualizer import TreeVisualizer
from datetime import datetime


class BombermanModel(Model):
    def __init__(
        self,
        width,
        height,
        map_data,
        pos_goal,
        pos_bomberman,
        number_of_agents,
        search_algorithm,
        priority,
        heuristic,
        powers,
        difficulty,
        rocks,
        pos_balloon,
        turn,
    ):
        super().__init__()
        self.width = width
        self.height = height
        self.num_agents = number_of_agents
        self.search_algorithm = search_algorithm
        self.heuristic = heuristic
        self.visited_cells = []
        self.final_path_cells = set()
        self.visited_ground_cells = set()
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = RandomActivation(self)
        self.running = True
        self.priority = priority
        self.pos_goal = pos_goal
        self.num_powers = powers
        self.rocks = rocks
        self.difficulty = difficulty
        self.destruction_power = 1
        self.create_map(map_data)
        self.turn = turn
        self.history = []
        self.history_length = 5

        self.bomberman = BombermanAgent(1, self, pos_bomberman)

        self.grid.place_agent(self.bomberman, self.bomberman.pos)

        self.schedule.add(self.bomberman)

        self.balloons = []
        for pos in pos_balloon:
            balloon = BalloonAgent(self.next_id(), self, pos)
            self.balloons.append(balloon)
            self.grid.place_agent(balloon, pos)
            self.schedule.add(balloon)

        if self.num_powers > len(self.rocks):
            self.num_powers = len(self.rocks)

        for _ in range(self.num_powers):
            x, y = random.choice(self.rocks)
            from agents import PowerAgent

            while any(
                isinstance(agent, PowerAgent)
                for agent in self.grid.get_cell_list_contents((x, y))
            ):
                x, y = random.choice(self.rocks)

            power = PowerAgent(self.next_id(), self, (x, y))
            self.grid.place_agent(power, (x, y))
            self.schedule.add(power)

    def create_map(self, map_data) -> None:
        """
        Crea el mapa del modelo a partir de los datos leídos de un archivo de texto.


        Args:
            map_data (list): Lista de listas con los datos del mapa.


        Returns:
            None
        """

        for y, row in enumerate(map_data):
            for x, terrain_type in enumerate(row):
                if (
                    terrain_type == GRASS
                    or terrain_type == BOMBERMAN
                    or terrain_type == BALLOON
                ):
                    cell = GrassAgent((x, y), self)
                elif terrain_type == ROCK:
                    cell = RockAgent((x, y), self)
                elif terrain_type == METAL:
                    cell = MetalAgent((x, y), self)
                elif terrain_type == BORDER:
                    cell = BorderAgent((x, y), self)
                elif terrain_type == GOAL:
                    cell = GoalAgent((x, y), self)
                else:
                    continue

                self.grid.place_agent(cell, (x, y))
                self.schedule.add(cell)

    def step(self):
        from agents.powerAgent import PowerAgent

        self.schedule.step()

        agents_in_cell = self.grid.get_cell_list_contents(self.bomberman.pos)

        for a in agents_in_cell:
            if isinstance(a, BalloonAgent):
                print("Bomberman ha sido derrotado")
                self.running = False

        # verificar si bomberman ha pasado por la posición del poder
        for agent in self.grid.get_cell_list_contents(self.bomberman.pos):
            if isinstance(agent, PowerAgent):
                print("################# Bomberman ha obtenido un poder ###########")
                self.destruction_power += 1
                self.grid.remove_agent(agent)
                self.schedule.remove(agent)
                break

        # Verificar si Bomberman ha llegado a la salida
        if self.bomberman.pos == self.pos_goal:
            self.running = False

        if self.search_algorithm == ALPHA_BETA:
            depth = 2 * self.difficulty
            alpha = -math.inf
            beta = math.inf

            visualizer = TreeVisualizer()  # Crear un visualizador de árbol
            # Decidir el mejor movimiento para Bomberman
            _, best_bomberman_move = self.minimax(
                depth,
                alpha,
                beta,
                True,
                self.bomberman.pos,
                [balloon.pos for balloon in self.balloons],
                visualizer=visualizer,  # Pasar el visualizador
            )

            # Guardar el árbol de búsqueda en un archivo
            filename = f"tree_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
            visualizer.save(filename)

            # Mover Bomberman
            if best_bomberman_move:
                self.visited_cells.append(self.bomberman.pos)
                self.bomberman.move_to(best_bomberman_move)

            for balloon in self.balloons:
                # Evaluar el mejor movimiento para cada globo de manera independiente
                _, best_balloon_move = self.minimax(
                    depth, alpha, beta, False, self.bomberman.pos, [balloon.pos]
                )  # Pasar solo la posición del globo actual
                if best_balloon_move:
                    balloon.move_to(
                        best_balloon_move
                    )  # Mover el globo a la posición determinada

            self.pruning_log = []  # Limpiar el registro de poda

            # Verificar si el juego ha terminado
            if self.game_over(
                self.bomberman.pos, [balloon.pos for balloon in self.balloons]
            ):
                self.running = False

    def next_id(self) -> int:
        return super().next_id()

    def minimax(
        self,
        depth,
        alpha,
        beta,
        is_maximizing_player,
        current_pos_bomberman,
        current_pos_balloons,
        previous_state=None,
        visualizer=None,
        parent=None,
    ):
        if depth == 0 or self.game_over(current_pos_bomberman, current_pos_balloons):
            heuristic_value = (
                self.heuristic_bomberman(current_pos_bomberman, current_pos_balloons)
                if is_maximizing_player
                else sum(
                    self.heuristic_balloon(current_pos_bomberman, balloon_pos)
                    for balloon_pos in current_pos_balloons
                )
            )
            label = f"Value: {heuristic_value}"
            if visualizer:
                visualizer.add_node(label, parent=parent)
            return heuristic_value, None

        best_move = None
        if is_maximizing_player:
            max_eval = -math.inf
            for move in self.get_possible_moves(
                current_pos_bomberman, is_maximizing_player
            ):
                label = f"Bomberman: {move}"
                node = visualizer.add_node(label, parent=parent) if visualizer else None

                eval, _ = self.minimax(
                    depth - 1,
                    alpha,
                    beta,
                    False,
                    move,
                    current_pos_balloons,
                    previous_state=previous_state,
                    visualizer=visualizer,
                    parent=node,
                )
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    if visualizer:
                        prune_label = f"({move[0]},{move[1]})"
                        visualizer.add_node(
                            prune_label,
                            parent=parent,
                            pruned=True,
                            prune_reason="Beta <= Alpha",
                        )
                    break
            return max_eval, best_move
        else:
            min_eval = math.inf
            for move in self.get_possible_moves(
                current_pos_balloons[0], not is_maximizing_player
            ):
                label = f"Balloon: {move}"
                node = visualizer.add_node(label, parent=parent) if visualizer else None

                eval, _ = self.minimax(
                    depth - 1,
                    alpha,
                    beta,
                    True,
                    current_pos_bomberman,
                    [move],
                    previous_state=previous_state,
                    visualizer=visualizer,
                    parent=node,
                )
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    if visualizer:
                        prune_label = f"({move[0]},{move[1]})"
                        visualizer.add_node(
                            prune_label,
                            parent=parent,
                            pruned=True,
                            prune_reason="Beta <= Alpha",
                        )
                    break
            return min_eval, best_move

    def heuristic_bomberman(
        self, current_pos_bomberman, current_pos_balloons, previous_state=None
    ):
        # Distancia a la meta
        dist_to_goal = self.manhattan_distance(current_pos_bomberman, self.pos_goal)

        # Calcular la distancia total a los globos
        dist_to_balloons = sum(
            self.manhattan_distance(current_pos_bomberman, balloon_pos)
            for balloon_pos in current_pos_balloons
        )

        # Calcular la distancia mínima a los globos
        min_dist_to_balloons = min(
            self.manhattan_distance(current_pos_bomberman, balloon_pos)
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

        if current_pos_bomberman in self.history:
            penalty += 20

        self.history.append(current_pos_bomberman)
        if len(self.history) > self.history_length:
            self.history.pop(0)

        # Combinar las diferentes penalizaciones y heurísticas
        return -dist_to_goal * 4 + dist_to_balloons * 5 - penalty - balloon_penalty

    def heuristic_balloon(self, current_pos_bomberman, current_pos_balloon):
        return self.manhattan_distance(current_pos_balloon, current_pos_bomberman)

    def get_possible_moves(self, current_pos, is_bomberman):
        # This method returns the valid neighboring positions
        neighbors = self.grid.get_neighborhood(
            current_pos, moore=False, include_center=False
        )
        valid_moves = []
        for neighbor in neighbors:
            if self.is_valid_move(neighbor, is_bomberman):
                valid_moves.append(neighbor)
        return valid_moves

    def is_valid_move(self, position, is_bomberman):
        # Verifica si un movimiento es válido
        cell = self.grid.get_cell_list_contents(position)

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

    def manhattan_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def game_over(self, current_pos_bomberman, current_pos_balloons):
        # Bomberman alcanza la meta o es atrapado por un globo
        if current_pos_bomberman == self.pos_goal:
            return True
        if any(current_pos_bomberman == pos for pos in current_pos_balloons):
            return True
        return False
