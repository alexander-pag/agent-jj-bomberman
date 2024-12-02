from mesa import Agent
from agents.bombermanAgent import BombermanAgent
from agents.rockAgent import RockAgent
from agents.metalAgent import MetalAgent
from agents.borderAgent import BorderAgent
from algorithms.alpha_beta import choose_best_move
import random


class BalloonAgent(Agent):
    def __init__(self, unique_id, model, start_pos):
        super().__init__(unique_id, model)
        self.pos = start_pos
        self.model = model

    def step(self):
        self.move_to(self.pos)

    def move(self):
        if self.model.turn != "Balloon":
            return  # No es el turno del globo

        initial_state = self.model.get_state()
        print("### MOVIMIENTO DE GLOBO ###")
        # Elegir el mejor movimiento y el nuevo estado simulado
        next_move, child_state = choose_best_move(self.model, initial_state, False)

        if next_move:
            print(f"--------------------------------- Moviendo Globo a {next_move}")
            self.model.grid.move_agent(self, next_move)
            self.pos = next_move
            self.detect_bomberman()
        else:
            print("No se encontró movimiento válido")
        self.model.turn = "Bomberman"

    def is_obstacle(self, pos):
        print(f"Checking position in is_obstacle: {pos}")  # Depuración
        if not isinstance(pos, tuple) or len(pos) != 2:
            raise ValueError(f"Invalid position format: {pos}")
        if self.model.grid.out_of_bounds(pos):
            return True

        # Obtener los agentes en la celda
        cellmates = self.model.grid.get_cell_list_contents([pos])
        for agent in cellmates:
            if (
                isinstance(agent, BorderAgent)
                or isinstance(agent, RockAgent)
                or isinstance(agent, MetalAgent)
            ):
                return True
        return False

    # detectar si hay un bomberman en la misma posición que el globo y terminar la simulación
    def detect_bomberman(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        for agent in cellmates:
            if isinstance(agent, BombermanAgent):
                print("¡Bomberman ha sido capturado!")
                self.model.running = False
                break

    def move_to(self, new_pos):
        if isinstance(new_pos, list):
            # Si new_pos es una lista de posiciones, movemos cada globo por separado
            for pos in new_pos:
                if not self.is_obstacle(pos):
                    self.model.grid.move_agent(self, pos)
                    self.pos = pos
                    self.detect_bomberman()
                    return True  # Si al menos uno se movió correctamente, retornamos True
        else:
            # Si es una sola posición, la movemos directamente
            if not self.is_obstacle(new_pos):
                self.model.grid.move_agent(self, new_pos)
                self.pos = new_pos
                self.detect_bomberman()
                return True

        return False  # Si no se pudo mover


    def move_randomly(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = random.choice(possible_steps)
        self.move_to(new_position)
        self.detect_bomberman()
        return True
