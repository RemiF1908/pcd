from .Command import Command
import json
from ..model.dungeon import Dungeon
from ..model.cell import Cell
from ..model.floor import Floor
from ..model.wall import Wall
from ..model.trap import Trap
from ..model.entity_factory import EntityFactory


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
                    entity = EntityFactory.create_floor()
                elif entity_type == "Wall":
                    entity = EntityFactory.create_wall()
                elif entity_type == "Trap":
                    damage = cell_data.get("damage", 10)
                    entity = EntityFactory.create_trap(damage=damage)
                elif entity_type == "Dragon":
                    entity = EntityFactory.create_dragon()
                elif entity_type == "Bombe":
                    entity = EntityFactory.create_bombe()
                else:
                    entity = Floor()
                entity.init_range(position)
                cell = Cell(position, entity)
                grid_row.append(cell)
            grid.append(grid_row)

        dungeon = Dungeon(dimension=dimension, entry=entry, exit=exit)
        dungeon.grid = grid
        self.result = dungeon
        print(f"Dungeon imported from {self.filepath}")
