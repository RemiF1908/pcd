#idée : clique droit sur une entité -> supprimer l'entité
from .Command import Command

class removeEntity(Command) :

    def __init__(self, dungeon, coord):
        self.dungeon = dungeon
        self.coord = coord

    def execute(self):
        cell = self.dungeon.get_cell(self.coord)
        if cell.entity is not None:
            cell.entity = None
            print(f"Entity removed from {self.coord}")
        else:
            print(f"No entity found at {self.coord}")