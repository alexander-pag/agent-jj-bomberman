from mesa import Agent
from agents.explosionAgent import ExplosionAgent
from agents.rockAgent import RockAgent
from agents.grassAgent import GrassAgent
from agents.metalAgent import MetalAgent
from agents.borderAgent import BorderAgent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BombAgent(Agent):
    def __init__(self, unique_id, model, power, pos):
        super().__init__(unique_id, model)
        self.power = power
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
        
        positions = [
            self.pos,
            (self.pos[0] + 1, self.pos[1]),
            (self.pos[0] - 1, self.pos[1]),
            (self.pos[0], self.pos[1] + 1),
            (self.pos[0], self.pos[1] - 1)
        ]
        
        # Filter valid positions and check for metal/border agents
        valid_positions = []
        for pos in positions:
            # Check grid boundaries
            if not (0 <= pos[0] < self.model.grid.width and 
                    0 <= pos[1] < self.model.grid.height):
                continue
                
            # Check cell contents
            cell_contents = self.model.grid.get_cell_list_contents(pos)
            if any(isinstance(agent, (MetalAgent, BorderAgent)) for agent in cell_contents):
                continue
                
            valid_positions.append(pos)

        # Process explosions for valid positions
        for pos in valid_positions:
            # Create explosion
            explosion = ExplosionAgent(self.model.next_id(), self.model)
            changes.append(('add_explosion', explosion, pos))
            
            # Handle rocks
            cell_contents = self.model.grid.get_cell_list_contents(pos)
            for agent in cell_contents:
                if isinstance(agent, RockAgent):
                    changes.append(('remove', agent, pos))
                    grass = GrassAgent(self.model.next_id(), self.model)
                    changes.append(('add_grass', grass, pos))

        # Apply changes atomically
        for action, agent, pos in changes:
            if action == 'remove':
                self.model.grid.remove_agent(agent)
                self.model.schedule.remove(agent)
            elif action in ['add_explosion', 'add_grass']:
                self.model.grid.place_agent(agent, pos)
                self.model.schedule.add(agent)