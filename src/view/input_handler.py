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
from src.commands.nextlevel import nextLevel

if TYPE_CHECKING:
    from src.model.simulation import Simulation
    from src.model.dungeon import Dungeon
    from src.model.campaign_manager import Campaign

class InputHandler:
    # CORRECTION 1: campaign est optionnel (= None) pour compatibilité
    def __init__(self, simulation: Simulation, dungeon: Dungeon, invoker: GameInvoker, campaign: Campaign = None):
        self.invoker = invoker
        self.simulation = simulation
        self.dungeon = dungeon
        self.campaign = campaign

    def start_wave(self) -> None:
        command = startWave(self.simulation)
        self.invoker.push_command(command)
        return self.invoker.execute()

    def stop_wave(self) -> None:
        command = stopWave(self.simulation)
        self.invoker.push_command(command)
        self.invoker.execute()

    def reset_dungeon(self) -> None:
        command = resetDungeon(self.dungeon, self.simulation)
        self.invoker.push_command(command)
        self.invoker.execute()

    def export_dungeon(self) -> None:
        command = exportDungeon(self.dungeon, "dungeon")
        self.invoker.push_command(command)
        self.invoker.execute()

    def import_dungeon(self) -> None:
        print("in importDungeon execute")
        command = importDungeon("dungeon")
        self.invoker.push_command(command)
        self.invoker.execute()
        res = command.result
        if res:
            self.simulation.dungeon = res
            self.dungeon = res # <--- Important : Mise à jour de la ref locale

    def place_trap(self, pos) -> None:
        # Note: Assurez-vous que create_trap accepte 'damage'. Sinon, retirez l'argument.
        try:
            trap = EntityFactory.create_trap(damage=10)
        except TypeError:
            trap = EntityFactory.create_trap()
            
        command = placeEntity(self.dungeon, trap, pos, self.simulation)
        self.invoker.push_command(command)
        self.invoker.execute()

    def place_wall(self, pos) -> None:
        wall = EntityFactory.create_wall()
        command = placeEntity(self.dungeon, wall, pos, self.simulation)
        self.invoker.push_command(command)
        self.invoker.execute()

    def place_dragon(self, pos, orientation=0) -> None: # orientation=0 par defaut
        dragon = EntityFactory.create_dragon(orientation=orientation)
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
        
    def load_next_level(self) -> None:
        if not self.campaign:
            print("Erreur: Pas de campagne chargée")
            return

        command = nextLevel(self.campaign, self.simulation)
        self.invoker.push_command(command)
        self.invoker.execute()
        
        # CORRECTION 2: Mise à jour des références après changement de niveau
        # On suppose que la commande nextLevel a mis à jour la simulation dans le controlleur
        if self.invoker.game_controller:
             self.simulation = self.invoker.game_controller.simulation
             self.dungeon = self.invoker.game_controller.dungeon
             print(f"InputHandler mis à jour sur le niveau {self.simulation.level.difficulty}")

    def update_dungeon(self, new_dungeon: Dungeon) -> None:
        self.dungeon = new_dungeon