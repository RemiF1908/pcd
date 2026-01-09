from .Command import Command
import json
from ..model.dungeon import Dungeon
from ..model.cell import Cell
from ..model.hero import Hero
from ..model.level import Level
from ..model.campaign_manager import Campaign

from ..model.entity_factory import EntityFactory


class importDungeon(Command):
    """Command to import a full level state from a JSON file."""

    def __init__(self, filename: str):
        self.filename = filename
        self.filepath = f"./save/{filename}.json"
        self.result = None
        self.campaign_progress = None

    def execute(self, game_controller) -> None:
        if not game_controller or not game_controller.simulation:
            print("Import failed: Simulation context is not available.")
            return

        with open(self.filepath, "r") as f:
            data = json.load(f)
        campaign = game_controller.campaign 
        # 1. Rebuild Dungeon
        dimension = tuple(data["dimension"])
        entry = tuple(data["entry"])
        exit_ = tuple(data["exit"])
        grid_data = data["grid"]
        grid = []
        for row_idx, row in enumerate(grid_data):
            grid_row = []
            for col_idx, cell_data in enumerate(row):
                entity_type = cell_data["type"]
                position = tuple(cell_data["position"])
                entity = None
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
                    entity = EntityFactory.create_floor()

                if entity:
                    entity.init_range(position)

                cell = Cell(position, entity)
                grid_row.append(cell)
            grid.append(grid_row)

        dungeon = Dungeon(dimension=dimension, entry=entry, exit=exit_)
        dungeon.grid = grid
      
        sim = game_controller.simulation
        level_id = data.get("level_id", sim.level.difficulty)
        level = game_controller.campaign.load_level(level_id)
        sim.level = level
        sim.dungeon = dungeon
        sim.current_budget = data["current_budget"]
        

        self.result = dungeon
