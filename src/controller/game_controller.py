import time
from typing import Optional, Any
from src.commands import placeEntity, exportDungeon, importDungeon, startWave, stopWave, resetDungeon


class GameController:
    """Orchestre la boucle principale : interface <-> simulation.

    - `interface` doit exposer au moins : `render(simulation)` et
      optionnellement `get_input()` / `handle_command(cmd, simulation)`.
    - `simulation` est une instance de `Simulation` (src/simulation.py)
      qui expose `step()` / `launch()` / `stop_condition()`.
    """

    def __init__(self, interface: Any, simulation: Any) -> None:
        self.interface = interface
        self.simulation = simulation

    def start_wave(self) -> None:
        """Démarre une nouvelle vague dans la simulation."""
        print("Starting new wave...")
        self.simulation.launch()

    def placeEntity(self, entity: Any, coord: tuple) -> None:
        placeEntity.placeEntity().place_entity(self.simulation.dungeon, entity, coord)
    def stop(self) -> None:
        """Arrête la boucle principale."""
        self.simulation.stop()
