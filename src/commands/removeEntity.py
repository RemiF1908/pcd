# idée : clique droit sur une entité -> supprimer l'entité
from .Command import Command
from ..model.floor import Floor


class removeEntity(Command):
    def __init__(self, dungeon, coord, simulation):
        self.dungeon = dungeon
        self.coord = coord
        self.simulation = simulation

    def execute(self, game_controller):
        if not(self.simulation.isSimStarted):
            cell = self.dungeon.get_cell(self.coord)
            
            entity_to_remove = cell.entity
            if not isinstance(entity_to_remove, Floor):
                if hasattr(entity_to_remove, 'cost'):
                    self.simulation.current_budget += entity_to_remove.cost
                cell.entity = Floor()
                print(f"Entity removed from {self.coord} and budget refunded.")


