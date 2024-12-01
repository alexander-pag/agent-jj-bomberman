from mesa import Agent
from agents.bombermanAgent import BombermanAgent
from agents.rockAgent import RockAgent
from agents.metalAgent import MetalAgent
from agents.borderAgent import BorderAgent
from algorithms.alpha_beta import choose_best_move


class BalloonAgent(Agent):
    def __init__(self, unique_id, model, start_pos):
        super().__init__(unique_id, model)
        self.pos = start_pos
        self.model = model

    def step(self):
        self.move()

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
        cellmates = self.model.grid.get_cell_list_contents([pos])
        for agent in cellmates:
            if (
                isinstance(agent, BorderAgent)
                or isinstance(agent, RockAgent)
                or isinstance(agent, MetalAgent)
                or isinstance(agent, BalloonAgent)
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
