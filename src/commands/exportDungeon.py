from .Command import Command
import json


class exportDungeon(Command):
    def __init__(self, dungeon, filename: str, campaign_progress=None):
        self.dungeon = dungeon
        self.filename = filename
        self.filepath="./save/"+filename + ".json"
        self.campaign_progress = campaign_progress

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

        # Ajouter la progression de campagne si disponible
        if self.campaign_progress is not None:
            dungeon_data["campaign_progress"] = self.campaign_progress

        with open(self.filepath, "w") as file:
            json.dump(dungeon_data, file, indent=2)
        print(f"Dungeon exported to {self.filepath}")
