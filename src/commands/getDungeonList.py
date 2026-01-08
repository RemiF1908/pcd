from .Command import Command
import json
from ..model.dungeon import Dungeon
from ..model.cell import Cell
from ..model.floor import Floor
from ..model.wall import Wall
from ..model.trap import Trap


class getDungeonList(Command):
    """Command to get the names of saved dungeons from the save directory."""

    def __init__(self):
        self.save_directory = "./save/"
        self.result = []

    def execute(self, game_controller) -> None:
        import os

        try:
            files = os.listdir(self.save_directory)
            dungeon_files = [
                f[:-5] for f in files if f.endswith(".json")
            ]  # Remove .json extension
            self.result = dungeon_files
            print(f"Dungeon list retrieved from {self.save_directory}")
        except FileNotFoundError:
            print(f"Save directory {self.save_directory} not found.")
            self.result = []
