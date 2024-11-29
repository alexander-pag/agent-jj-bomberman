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
    PowerAgent
)
from config.constants import *
from algorithms.alpha_beta import manhattan_distance
import random

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

        self.bomberman = BombermanAgent(1, self, pos_bomberman)

        self.grid.place_agent(self.bomberman, self.bomberman.pos)

        self.schedule.add(self.bomberman)

        # añadir los globos al modelo
        self.balloon = BalloonAgent(self.next_id(), self, pos_balloon)

        self.grid.place_agent(self.balloon, self.balloon.pos)

        self.schedule.add(self.balloon)
        
        
        # colocar poderes aleatorios debajo de las rocas
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

    def step(self) -> None:
        self.schedule.step()

        agents_in_cell = self.grid.get_cell_list_contents(self.bomberman.pos)

        for a in agents_in_cell:
            if isinstance(a, BalloonAgent):
                print("Bomberman ha sido derrotado")
                self.running = False

        # Verificar si Bomberman ha llegado a la salida
        if self.bomberman.pos == self.pos_goal:
            self.running = False
            
        # verificar si bomberman ha pasado por la posición del poder
        for agent in self.grid.get_cell_list_contents(self.bomberman.pos):
            if isinstance(agent, PowerAgent):
                print("################# Bomberman ha obtenido un poder ###########")
                self.destruction_power += 1
                self.grid.remove_agent(agent)
                self.schedule.remove(agent)
                break

    def throw_bomb(self, current_pos, target_pos):
        """Destruye una roca y muestra animación de bomba"""
        cell_contents = self.grid.get_cell_list_contents(target_pos)
        rock_found = any(isinstance(agent, RockAgent) for agent in cell_contents)

        if rock_found:
            # Primero remover la roca
            for agent in cell_contents:
                if isinstance(agent, RockAgent):
                    self.grid.remove_agent(agent)
                    break
            from agents import BombAgent

            # Crear y colocar bomba en la posición del objetivo
            bomb = BombAgent(self.next_id(), self, target_pos)
            self.grid.place_agent(bomb, target_pos)

            # Crear césped después de un breve delay
            grass_agent = GrassAgent(target_pos, self)
            self.grid.place_agent(grass_agent, target_pos)
            self.schedule.add(grass_agent)

            # La bomba debe aparecer en una capa superior
            return bomb  # Retornamos la bomba para poder eliminarla después

    def next_id(self) -> int:
        return super().next_id()

    def get_state(self):
        state = [["X" for _ in range(self.width)] for _ in range(self.height)]
        
        # Primero asignamos las posiciones de Bomberman (S) y Enemigos (B)
        for agent in self.schedule.agents:
            if 0 <= agent.pos[0] < self.width and 0 <= agent.pos[1] < self.height:
                current_pos = state[agent.pos[1]][agent.pos[0]]
                
                # Asignar primero Bomberman (S)
                if isinstance(agent, BombermanAgent):
                    if current_pos == "X":  # Solo asignar si está vacío
                        state[agent.pos[1]][agent.pos[0]] = "S"
                
                # Asignar luego los enemigos (B)
                elif isinstance(agent, BalloonAgent):
                    if current_pos == "X":  # Solo asignar si está vacío
                        state[agent.pos[1]][agent.pos[0]] = "B"
        
        # Luego asignamos el resto de los agentes (si no ocupan las casillas de Bomberman ni enemigos)
        for agent in self.schedule.agents:
            if 0 <= agent.pos[0] < self.width and 0 <= agent.pos[1] < self.height:
                current_pos = state[agent.pos[1]][agent.pos[0]]
                
                # Solo asignar si la casilla está vacía
                if current_pos == "X":
                    if isinstance(agent, GoalAgent):
                        state[agent.pos[1]][agent.pos[0]] = "G"
                    elif isinstance(agent, RockAgent):
                        state[agent.pos[1]][agent.pos[0]] = "R"
                    elif isinstance(agent, GrassAgent):
                        state[agent.pos[1]][agent.pos[0]] = "C"
                    elif isinstance(agent, MetalAgent):
                        state[agent.pos[1]][agent.pos[0]] = "M"
        
        print(f"Estado generado: {state}")  # Debug para asegurarse de que es una lista de listas
        return state

    def get_agent_positions(self):
        positions = {}
        for agent in self.schedule.agents:
            if agent.__class__.__name__ == "BombermanAgent":
                positions["S"] = agent.pos
            elif agent.__class__.__name__ == "BalloonAgent":
                positions["B"] = agent.pos
        return positions

    def simulate_move(self, state, actor, new_pos):
        """
        Simula el movimiento de un actor (Bomberman o enemigo) en el estado dado.
        """
        current_pos = self.find_position(state, actor)
        new_state = [row[:] for row in state]  # Copiar el estado
        if current_pos:
            new_state[current_pos[1]][current_pos[0]] = "C"  # Limpia la posición actual
        new_state[new_pos[1]][new_pos[0]] = actor
        return new_state

    def get_possible_states(self, state, agent):
        # Obtener la posición del agente a partir de la clave ('S' para Bomberman, por ejemplo)
        agent_pos = self.get_agent_positions().get("S")  # Aquí podemos asumir que "S" es la clave para Bomberman
        possible_states = []
        
        for move in self.possible_moves(agent):
            # Verificar si el movimiento es válido
            if self.is_valid_move(move, state):
                # Crear una copia del estado actual
                new_state = [row[:] for row in state]
                
                # Limpiar la posición actual del agente (asumimos que 'C' es césped/espacio vacío)
                new_state[agent_pos[1]][agent_pos[0]] = 'C'
                
                # Verificar si la nueva posición está ocupada por un obstáculo o un agente no deseado
                current_cell = new_state[move[1]][move[0]]
                if current_cell in ['R', 'B', 'M', 'X']:  # 'R' = roca, 'B' = enemigo, 'M' = metal
                    continue  # No se puede mover a esa celda

                # Colocar el agente en la nueva posición
                new_state[move[1]][move[0]] = 'S'  # Colocar Bomberman ('S') en la nueva posición
                
                # Agregar el nuevo estado al listado de posibles
                possible_states.append((new_state, move))  # Añadir también la nueva posición
        
        return possible_states


    
    def possible_moves(self,agent):
        agent_pos = self.get_agent_positions()[agent]
        # Aquí deberías definir los posibles movimientos según las reglas del juego
        moves = [
            (agent_pos[0] + 1, agent_pos[1]),  # mover a la derecha
            (agent_pos[0] - 1, agent_pos[1]),  # mover a la izquierda
            (agent_pos[0], agent_pos[1] + 1),  # mover abajo
            (agent_pos[0], agent_pos[1] - 1),  # mover arriba
        ]
        return moves

    def is_valid_move(self, move, state):
        # Comprobar si la nueva posición está dentro de los límites del tablero
        if not (0 <= move[0] < len(state[0]) and 0 <= move[1] < len(state)):
            return False
        
        # Comprobar si la casilla está ocupada por un obstáculo o un agente no deseado (ej. una roca o un enemigo)
        # Puedes ajustar la lógica aquí dependiendo de los elementos en el tablero
        if state[move[1]][move[0]] in ['R', 'B', 'M', 'X']:  # 'R' = roca, 'B' = enemigo, 'M' = metal
            return False
        
        return True

    
    def find_position(self, state, actor):
        """
        Encuentra la posición del actor en el estado dado.
        """
        # Traducir el nombre del actor a su símbolo
        actor_symbol = ACTOR_SYMBOLS.get(actor)
        if actor_symbol is None:
            raise ValueError(f"Actor desconocido: {actor}. Verifica el mapeo ACTOR_SYMBOLS.")

        #print(f"Debug - Tablero recibido en find_position:")
        #for row in state:
        #    print(" ".join(row))
        #print(f"Debug - Buscando símbolo del actor: {actor_symbol}")

        # Buscar el símbolo en el tablero
        for y, row in enumerate(state):
            for x, cell in enumerate(row):
                #print(f"Debug - Evaluando celda ({x}, {y}): {cell}")
                if cell == actor_symbol:
                    #print(f"Debug - Actor encontrado en posición: ({x}, {y})")
                    return (x, y)
            
        print(f"Error: Actor '{actor}' no encontrado en el tablero.")
        return None

    def is_terminal_state(self,state):
        bomberman_pos = self.find_position(state, "S")
        goal_pos = self.find_position(state, "G")
        enemy_pos = self.find_position(state, "B")
        return bomberman_pos == goal_pos or bomberman_pos == enemy_pos
    
    def evaluate_state(self,state, maximizing_player):
        """
        Evalúa el estado actual del juego con una heurística multifactorial.
        """
        bomberman_pos = self.find_position(state, "S")
        goal_pos = self.find_position(state, "G")
        enemy_pos = self.find_position(state, "B")

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