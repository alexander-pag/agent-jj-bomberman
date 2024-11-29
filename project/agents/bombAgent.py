from mesa import Agent
from agents.borderAgent import BorderAgent
from agents.explosionAgent import ExplosionAgent
from agents.grassAgent import GrassAgent
from agents.metalAgent import MetalAgent
from agents.rockAgent import RockAgent
import logging
from collections import deque

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BombAgent(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.power = model.destruction_power
        self.cooldown = 2
        self.pos = pos

    def step(self):
        self.cooldown -= 1
        if self.cooldown <= 0:
            self.explode()
            self.model.schedule.remove(self)
            self.model.grid.remove_agent(self)

    def explode(self):
        # Create list to track changes
        changes = []

        # Initialize BFS queue with the starting position and distance 0
        queue = deque([(self.pos, 0)])
        visited = set()  # Track visited cells to avoid processing them multiple times

        while queue:
            current_pos, distance = queue.popleft()

            # Skip positions already visited
            if current_pos in visited:
                continue
            visited.add(current_pos)

            # Check grid boundaries
            if not (
                0 <= current_pos[0] < self.model.grid.width
                and 0 <= current_pos[1] < self.model.grid.height
            ):
                continue

            # Check cell contents
            cell_contents = self.model.grid.get_cell_list_contents(current_pos)
            if any(isinstance(agent, (MetalAgent, BorderAgent)) for agent in cell_contents):
                continue

            # Handle rocks
            rock_found = False
            for agent in cell_contents:
                if isinstance(agent, RockAgent):
                    changes.append(("remove", agent, current_pos))
                    grass = GrassAgent(self.model.next_id(), self.model)
                    changes.append(("add_grass", grass, current_pos))
                    rock_found = True  # Stop propagation beyond this point
                    break

            # Add explosion to the current position
            explosion = ExplosionAgent(self.model.next_id(), self.model)
            changes.append(("add_explosion", explosion, current_pos))

            # Stop further exploration if a rock was found or max distance is reached
            if rock_found or distance >= self.power:
                continue

            # Add neighboring positions to the queue for further exploration
            neighbors = [
                (current_pos[0] + 1, current_pos[1]),
                (current_pos[0] - 1, current_pos[1]),
                (current_pos[0], current_pos[1] + 1),
                (current_pos[0], current_pos[1] - 1),
            ]
            for neighbor in neighbors:
                if neighbor not in visited:
                    queue.append((neighbor, distance + 1))

        # Apply changes atomically
        for action, agent, pos in changes:
            if action == "remove":
                self.model.grid.remove_agent(agent)
                self.model.schedule.remove(agent)
            elif action in ["add_explosion", "add_grass"]:
                self.model.grid.place_agent(agent, pos)
                self.model.schedule.add(agent)