from .Command import Command
from src.model.hero import Hero
from src.simulation import Simulation


class startWave(Command):
    def __init__(self, simulation):
        self.simulation : Simulation = simulation

    def execute(self, game_controller):
        if not(self.simulation.isSimStarted):
            self.simulation.isSimStarted = True
            for h in self.simulation.heroes:
                # S'assurer que le héros est à la position d'entrée
                h.coord = self.simulation.dungeon.entry
                h.compute_path(self.simulation.dungeon, self.simulation.dungeon.entry, self.simulation.dungeon.exit)
                assert h.path is not None
                # Réveiller le héros pour qu'il soit visible
                h.awake()
        return self.simulation.step()
