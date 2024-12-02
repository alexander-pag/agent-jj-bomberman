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
        self.history = []  # Historial de posiciones recientes del Bomberman
        self.history_length = 5  # Longitud del historial, ajustable

        self.bomberman = BombermanAgent(1, self, pos_bomberman)

        self.grid.place_agent(self.bomberman, self.bomberman.pos)

        self.schedule.add(self.bomberman)

        self.balloons = []  # Lista para almacenar múltiples globos
        for pos in pos_balloon:  # Recorrer la lista de posiciones
            balloon = BalloonAgent(self.next_id(), self, pos)
            self.balloons.append(balloon)
            self.grid.place_agent(balloon, pos)
            self.schedule.add(balloon)

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
        depth = 6
        alpha = -math.inf
        beta = math.inf

        # Decidir el mejor movimiento para Bomberman
        _, best_bomberman_move = self.minimax(
            depth, alpha, beta, True, self.bomberman.pos, [balloon.pos for balloon in self.balloons]
        )

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
                balloon.move_to(best_balloon_move)  # Mover el globo a la posición determinada



        # Verificar si el juego ha terminado
        if self.game_over(self.bomberman.pos, [balloon.pos for balloon in self.balloons]):
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
    ):
        # Verifica el formato de current_pos_balloons antes de pasarlo a minimax
        #print(f"Tipo de current_pos_balloons: {type(current_pos_balloons)}")
        #print(f"Contenido de current_pos_balloons: {current_pos_balloons}")

        if depth == 0 or self.game_over(current_pos_bomberman, current_pos_balloons):
            if is_maximizing_player:
                return (
                    self.heuristic_bomberman(
                        current_pos_bomberman, current_pos_balloons, previous_state
                    ),
                    None,
                )
            else:
                # Balloon heuristic: sum of distances to Bomberman
                return (
                    sum(
                        self.heuristic_balloon(current_pos_bomberman, balloon_pos)
                        for balloon_pos in current_pos_balloons
                    ),
                    None,
                )

        # Get the possible moves for Bomberman and Balloon
        bomberman_moves = self.get_possible_moves(
            current_pos_bomberman, is_maximizing_player
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
                    current_pos_balloons,  # Pasar todas las posiciones de los globos
                    previous_state=(current_pos_bomberman, current_pos_balloons),  # Pasar el estado anterior completo
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
            best_move = None  # Necesitas inicializar best_move para los globos correctamente
            for balloon_idx, balloon_pos in enumerate(current_pos_balloons):
                for move in self.get_possible_moves(balloon_pos, not is_maximizing_player):
                    new_positions = current_pos_balloons.copy()  # Copia la lista de posiciones de los globos
                    new_positions[balloon_idx] = move  # Actualiza la posición del globo correspondiente
                    eval, _ = self.minimax(
                        depth - 1,
                        alpha,
                        beta,
                        True,
                        current_pos_bomberman,
                        new_positions,  # Pasar las nuevas posiciones de los globos
                        previous_state=(current_pos_bomberman, current_pos_balloons),  # Estado previo
                    )
                    if eval < min_eval:
                        min_eval = eval
                        best_move = new_positions  # Guardar el mejor conjunto de posiciones
                    elif eval == min_eval:  # Si hay empate, selecciona aleatoriamente
                        best_move = random.choice([best_move, new_positions])
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
            return min_eval, best_move  # Aquí debes retornar el conjunto de movimientos de los globos




    def heuristic_bomberman(self, current_pos_bomberman, current_pos_balloons, previous_state=None):
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
        if not is_bomberman and any(isinstance(agent, BombermanAgent) for agent in cell):
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


