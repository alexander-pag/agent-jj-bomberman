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
    PowerAgent,
)
from config.constants import *
from algorithms.alpha_beta import manhattan_distance
from algorithms.astar import astar_search
import random
import math


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
        rocks,
        pos_balloon,
        turn,
    ):
        super().__init__()
        self.width = width  # Almacenar el ancho
        self.height = height  # Almacenar la altura
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
        self.destruction_power = 1
        self.create_map(map_data)
        self.turn = turn

        self.bomberman = BombermanAgent(1, self, pos_bomberman)

        self.grid.place_agent(self.bomberman, self.bomberman.pos)

        self.schedule.add(self.bomberman)

        # añadir los globos al modelo
        self.balloon = BalloonAgent(self.next_id(), self, pos_balloon)

        self.grid.place_agent(self.balloon, self.balloon.pos)

        self.schedule.add(self.balloon)

        # colocar poderes aleatorios debajo de las rocas
        if self.num_powers > len(self.rocks):
            # añadir el número de poderes que se pueda
            self.num_powers = len(self.rocks)

        for _ in range(self.num_powers):
            x, y = random.choice(self.rocks)
            from agents import PowerAgent

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

                # Colocar el agente en la posición correcta
                self.grid.place_agent(cell, (x, y))
                self.schedule.add(cell)

    def step(self):
        depth =6
        alpha = -math.inf
        beta = math.inf
        _, best_bomberman_move = self.minimax(
            depth, alpha, beta, True, self.bomberman.pos, self.balloon.pos
        )
        _, best_balloon_move = self.minimax(
            depth, alpha, beta, False, self.bomberman.pos, self.balloon.pos
        )

        # Move Bomberman and Balloon
        if best_bomberman_move:
            self.visited_cells.append(self.bomberman.pos)  # Registrar celda visitada
            self.bomberman.move_to(best_bomberman_move)
        if best_balloon_move:
            self.balloon.move_to(best_balloon_move)

        # Check game over
        if self.game_over(self.bomberman.pos, self.balloon.pos):
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
        current_pos_balloon,
        previous_state=None,  # Se agrega este argumento para el estado anterior
    ):
        # Base case: check if we have reached a terminal state (max depth, Bomberman has won or lost)
        if depth == 0 or self.game_over(current_pos_bomberman, current_pos_balloon):
            if is_maximizing_player:
                return (
                    self.heuristic_bomberman(
                        current_pos_bomberman, current_pos_balloon, previous_state
                    ),
                    None,
                )
            else:
                return (
                    self.heuristic_balloon(current_pos_bomberman, current_pos_balloon),
                    None,
                )

        # Get the possible moves for Bomberman and Balloon
        bomberman_moves = self.get_possible_moves(
            current_pos_bomberman, is_maximizing_player
        )
        balloon_moves = self.get_possible_moves(
            current_pos_balloon, not is_maximizing_player
        )

        best_move = None
        if is_maximizing_player:  # Bomberman (Maximizer)
            max_eval = -math.inf
            for move in bomberman_moves:
                eval, _ = self.minimax(
                    depth - 1,
                    alpha,
                    beta,
                    False,
                    move,  # New position of Bomberman
                    current_pos_balloon,
                    previous_state=(current_pos_bomberman, current_pos_balloon),  # Pasar el estado anterior
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
        else:  # Balloon (Minimizer)
            min_eval = math.inf
            for move in balloon_moves:
                eval, _ = self.minimax(
                    depth - 1,
                    alpha,
                    beta,
                    True,
                    current_pos_bomberman,
                    move,  # New position of Balloon
                    previous_state=(current_pos_bomberman, current_pos_balloon),  # Pasar el estado anterior
                )
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                elif eval == min_eval:  # Si hay empate, selecciona aleatoriamente
                    best_move = random.choice([best_move, move])
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move


    def heuristic_bomberman(self, current_pos_bomberman, current_pos_balloon, previous_state=None):
        dist_to_goal = self.manhattan_distance(current_pos_bomberman, self.pos_goal)
        dist_to_balloon = self.manhattan_distance(current_pos_bomberman, current_pos_balloon)

        penalty = 0
        if previous_state is not None:
            # Penalizar si estamos repitiendo el estado
            if (current_pos_bomberman, current_pos_balloon) == previous_state:
                penalty = 10  # Puedes ajustar el valor de la penalización

        return -dist_to_goal * 4 + dist_to_balloon * 5 - penalty



    def heuristic_balloon(self, current_pos_bomberman, current_pos_balloon):
        # Heuristic for Balloon: distance to Bomberman
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
        # Check if a move is valid based on the terrain and whether it's Bomberman or Balloon
        cell = self.grid.get_cell_list_contents(position)
        if any(isinstance(agent, BorderAgent) for agent in cell):
            return False
        if any(isinstance(agent, MetalAgent) for agent in cell):
            return False
        if is_bomberman and any(isinstance(agent, BalloonAgent) for agent in cell):
            return False
        return True

    def manhattan_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def game_over(self, current_pos_bomberman, current_pos_balloon):
        # Check if the game is over: Bomberman reaches the goal or is caught by the Balloon
        if current_pos_bomberman == self.pos_goal:
            return True
        if current_pos_bomberman == current_pos_balloon:
            return True
        return False
