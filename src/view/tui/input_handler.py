
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
    from src.view.tui.simulation_display import TUIView


class InputHandler:
    def __init__(self, tui_view: TUIView, invoker: GameInvoker):
        self.tui_view = tui_view
        self.invoker = invoker
        self.simulation = tui_view.simulation
        self.dungeon = tui_view.dungeon

    def _move_cursor(self, delta_row: int, delta_col: int) -> None:
        "Déplace le curseur selon les deltas fournis."
        row, col = self.tui_view.cursor_pos
        max_row, max_col = self.tui_view.dimension[0] - 1, self.tui_view.dimension[1] - 1
        new_row = max(0, min(max_row, row + delta_row))
        new_col = max(0, min(max_col, col + delta_col))
        self.tui_view.cursor_pos = (new_row, new_col)

    def move_cursor_up(self) -> None:
        self._move_cursor(-1, 0)

    def move_cursor_down(self) -> None:
        self._move_cursor(1, 0)

    def move_cursor_left(self) -> None:
        self._move_cursor(0, -1)

    def move_cursor_right(self) -> None:
        self._move_cursor(0, 1)

    def quit(self) -> None:
        self.tui_view.running = False

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

    def place_trap(self) -> None:
        trap = EntityFactory.create_trap(damage=10)
        command = placeEntity(self.dungeon, trap, self.tui_view.cursor_pos, self.simulation)
        self.invoker.push_command(command)
        self.invoker.execute()

    def place_wall(self) -> None:
        wall = EntityFactory.create_wall()
        command = placeEntity(self.dungeon, wall, self.tui_view.cursor_pos, self.simulation)
        self.invoker.push_command(command)
        self.invoker.execute()

    def place_dragon(self) -> None:
        dragon = EntityFactory.create_dragon()
        command = placeEntity(self.dungeon, dragon, self.tui_view.cursor_pos, self.simulation)
        self.invoker.push_command(command)
        self.invoker.execute()

    def place_bombe(self) -> None:
        bombe = EntityFactory.create_bombe()
        command = placeEntity(self.dungeon, bombe, self.tui_view.cursor_pos, self.simulation)
        self.invoker.push_command(command)
        self.invoker.execute()

    def remove_entity(self) -> None:
        command = removeEntity(self.dungeon, self.tui_view.cursor_pos, self.simulation)
        self.invoker.push_command(command)
        self.invoker.execute()
