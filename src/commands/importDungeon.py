from .Command import Command
import json
from ..model.dungeon import Dungeon
from ..model.cell import Cell
from ..model.hero import Hero
from ..model.level import Level
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

        # 1. Rebuild Dungeon
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

        dungeon = Dungeon(dimension=dimension, entry=entry, exit=exit)
        dungeon.grid = grid

        # 2. Rebuild Heroes
        heroes_data = data.get("heroes", [])
        new_heroes = []
        for hero_data in heroes_data:
            hero = Hero(
                pv_total=hero_data["pv_total"],
                strategy=hero_data["strategy"],
                coord=tuple(hero_data["position"])
            )
            hero.pv_cur = hero_data["pv_current"]
            new_heroes.append(hero)

        # 3. Create new Level and update Simulation state
        sim = game_controller.simulation
        level_id = data.get("level_id", sim.level.difficulty)

        # Create a new Level object to ensure a clean state
        new_level = Level(
            dungeon=dungeon,
            difficulty=level_id,
            heroes=new_heroes,
            budget_tot=sim.level.budget_tot  # Budget is not saved, so keep the current one
        )

        sim.level = new_level
        sim.dungeon = new_level.dungeon
        sim.heroes = new_level.heroes
        sim.current_budget = new_level.budget_tot

        

        print(f"Level and Dungeon state imported from {self.filepath}")
        self.result = None
