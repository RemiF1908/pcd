from .Command import Command
import json


class exportDungeon(Command):
    def __init__(self, dungeon, filename: str):
        self.dungeon = dungeon
        self.filename = filename
        self.filepath="./save/"+filename + ".json"

    def execute(self, game_controller):
        dungeon_data = {
            "dimension": self.dungeon.dimension,
            "entry": self.dungeon.entry,
            "exit": self.dungeon.exit,
            "grid": [],
        }
        for row in self.dungeon.grid:
            row_data = []
            for cell in row:
                entity_info = {
                    "type": type(cell.entity).__name__,
                    "position": cell.position,
                }
                if hasattr(cell.entity, "damage"):
                    entity_info["damage"] = cell.entity.damage
                row_data.append(entity_info)
            dungeon_data["grid"].append(row_data)

        with open(self.filepath, "w") as file:
            json.dump(dungeon_data, file, indent=2)
        print(f"Dungeon exported to {self.filepath}")
