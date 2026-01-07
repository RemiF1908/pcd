from .Command import Command
import json
from ..model.dungeon import Dungeon
from ..model.cell import Cell
from ..model.floor import Floor
from ..model.wall import Wall
from ..model.trap import Trap


class importDungeon(Command):
    """Command to import a dungeon from a JSON file."""

    def __init__(self, filename: str):
        self.filename = filename
        self.filepath = f"./save/{filename}.json"
        self.result = None

    def execute(self, game_controller) -> None:
        with open(self.filepath, "r") as f:
            data = json.load(f)

        dimension = tuple(data["dimension"])
        entry = tuple(data["entry"])
        exit = tuple(data["exit"])
        grid_data = data["grid"]

        grid = []
        for row_idx, row in enumerate(grid_data):
            grid_row = []
            for col_idx, cell_data in enumerate(row):
                entity_type = cell_data["type"]
                position = tuple(cell_data["position"])

                if entity_type == "Floor":
                    entity = Floor()
                elif entity_type == "Wall":
                    entity = Wall()
                elif entity_type == "Trap":
                    damage = cell_data.get("damage", 10)
                    entity = Trap(damage=damage)
                else:
                    entity = Floor()

                cell = Cell(position, entity)
                grid_row.append(cell)
            grid.append(grid_row)

        dungeon = Dungeon(dimension=dimension, entry=entry, exit=exit)
        dungeon.grid = grid
        self.result = dungeon
        print(f"Dungeon imported from {self.filepath}")
