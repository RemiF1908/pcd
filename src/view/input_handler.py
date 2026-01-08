
from __future__ import annotations
from typing import TYPE_CHECKING
from src.commands import *
from src.commands.GameInvoker import GameInvoker
from src.commands.startWave import startWave
from src.commands.stopWave import stopWave
from src.commands.resetDungeon import resetDungeon
from src.commands.placeEntity import placeEntity
from src.commands.removeEntity import removeEntity
from src.commands.exportDungeon import exportDungeon
from src.commands.importDungeon import importDungeon
from src.model.entity_factory import EntityFactory

if TYPE_CHECKING:
    from src.model.simulation import Simulation
    from src.model.dungeon import Dungeon


class InputHandler:
    def __init__(self, simulation: Simulation, dungeon: Dungeon, invoker: GameInvoker):
        self.invoker = invoker
        self.simulation = simulation
        self.dungeon = dungeon

    def start_wave(self) -> None:
        command = startWave(self.simulation)
        self.invoker.push_command(command)
        self.invoker.execute()

    def stop_wave(self) -> None:
        command = stopWave(self.simulation)
        self.invoker.push_command(command)
        self.invoker.execute()

    def reset_dungeon(self) -> None:
        command = resetDungeon(self.dungeon)
        self.invoker.push_command(command)
        self.invoker.execute()

    def export_dungeon(self) -> None:
        command = exportDungeon(self.dungeon, "dungeon.json")
        self.invoker.push_command(command)
        self.invoker.execute()

    def import_dungeon(self) -> None:
        command = importDungeon("dungeon.json")
        self.invoker.push_command(command)
        self.invoker.execute()

    def place_trap(self, pos) -> None:
        trap = EntityFactory.create_trap(damage=10)
        command = placeEntity(self.dungeon, trap, pos, self.simulation)
        self.invoker.push_command(command)
        self.invoker.execute()

    def place_wall(self, pos) -> None:
        wall = EntityFactory.create_wall()
        command = placeEntity(self.dungeon, wall, pos, self.simulation)
        self.invoker.push_command(command)
        self.invoker.execute()

    def place_dragon(self, pos) -> None:
        dragon = EntityFactory.create_dragon()
        command = placeEntity(self.dungeon, dragon, pos, self.simulation)
        self.invoker.push_command(command)
        self.invoker.execute()

    def place_bombe(self, pos) -> None:
        bombe = EntityFactory.create_bombe()
        command = placeEntity(self.dungeon, bombe, pos, self.simulation)
        self.invoker.push_command(command)
        self.invoker.execute()

    def remove_entity(self, pos) -> None:
        command = removeEntity(self.dungeon, pos, self.simulation)
        self.invoker.push_command(command)
        self.invoker.execute()
