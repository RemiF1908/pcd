import time
from typing import Optional, Any
from ..commands.GameInvoker import GameInvoker
from ..commands.startWave import startWave
from ..commands.stopWave import stopWave
from ..commands.resetDungeon import resetDungeon
from ..commands.placeEntity import placeEntity
from ..commands.removeEntity import removeEntity
from ..commands.exportDungeon import exportDungeon
from ..commands.importDungeon import importDungeon
from ..commands.getDungeonList import getDungeonList
from ..model.entity_factory import EntityFactory
from ..model.trap import Trap
from ..model.wall import Wall


class GameController:
    """Orchestre la boucle principale : interface <-> simulation.

    - `interface` doit exposer au moins : `render(simulation)` et
      optionnellement `get_input()` / `handle_command(cmd, simulation)`.
    - `simulation` est une instance de `Simulation` (src/simulation.py)
      qui expose `step()` / `launch()` / `stop_condition()`.

    Note: La gestion des niveaux/campagnes est déléguée à LevelController.
    """

    def __init__(self, interface: Any, simulation: Any) -> None:
        self.interface = interface
        self.simulation = simulation
        self.invoker = GameInvoker()

    @property
    def dungeon(self) -> Any:
        return self.simulation.dungeon

    def start_wave(self) -> None:
        """Démarre une nouvelle vague dans la simulation."""
        print("Starting new wave...")
        command = startWave(self.simulation)
        self.invoker.push_command(command)
        self.invoker.execute()

    def stop(self) -> None:
        """Arrête la boucle principale."""
        command = stopWave(self.simulation)
        self.invoker.push_command(command)
        self.invoker.execute()

    def reset_dungeon(self) -> None:
        """Réinitialise le donjon."""
        command = resetDungeon(self.dungeon)
        self.invoker.push_command(command)
        self.invoker.execute()

    def place_trap(self, position: tuple[int, int], damage: int = 10) -> None:
        """Place un piège à la position donnée."""
        trap = EntityFactory.create_trap(damage=damage)
        command = placeEntity(self.dungeon, trap, position)
        self.invoker.push_command(command)
        self.invoker.execute()

    def place_wall(self, position: tuple[int, int]) -> None:
        """Place un mur à la position donnée."""
        wall = EntityFactory.create_wall()
        command = placeEntity(self.dungeon, wall, position)
        self.invoker.push_command(command)
        self.invoker.execute()

    def remove_entity(self, position: tuple[int, int]) -> None:
        """Supprime l'entité à la position donnée."""
        command = removeEntity(self.dungeon, position)
        self.invoker.push_command(command)
        self.invoker.execute()

    def export_dungeon(self, filename: str = "dungeon") -> None:
        """Exporte le donjon dans un nom"""
        command = exportDungeon(self.dungeon, filename)
        self.invoker.push_command(command)
        self.invoker.execute()

    def import_dungeon(self, filepath: str = "dungeon"):
        """Importe le donjon depuis nom"""
        command = importDungeon(filepath)
        self.invoker.push_command(command)
        self.invoker.execute()
        imported_dungeon = command.result
        if imported_dungeon:
            self.simulation.dungeon = imported_dungeon
        return imported_dungeon

    def getDungeonList(self):
        """donne la liste des donjons sauvegardés"""
        command = getDungeonList()
        self.invoker.push_command(command)
        self.invoker.execute()
        return command.result

    def setup_level(self, level: Any) -> None:
        """Configure la simulation avec un niveau donné.

        Args:
            level: Instance de Level avec dungeon, budget, heroes, etc.
        """
        self.simulation.level = level
        self.simulation.dungeon = level.dungeon
        self.simulation.heroes = level.heroes
        self.simulation.current_budget = level.budget_tot
        self.simulation.reset()
