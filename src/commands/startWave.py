from .Command import Command
from src.model.hero import Hero
from src.simulation import Simulation


class startWave(Command):
    def __init__(self, simulation):
        self.simulation : Simulation = simulation

    def execute(self, game_controller):
        if not (self.simulation.isSimStarted):
            # Tentative de démarrage : calcule les chemins pour chaque héros.
            # Ne marque la simulation comme démarrée que si tous les héros ont un chemin.
            failed = False
            for h in self.simulation.heroes:
                # S'assurer que le héros est à la position d'entrée
                h.coord = self.simulation.dungeon.entry
                h.compute_path(
                    self.simulation.dungeon, self.simulation.dungeon.entry, self.simulation.dungeon.exit
                )
                if h.path == []:
                    failed = True
                    break

            if failed:
                # Ne pas laisser isSimStarted à True si le démarrage échoue
                self.simulation.isSimStarted = False
                return False

            # Tous les héros ont un chemin donc on peut démarrer
            self.simulation.isSimStarted = True
        return self.simulation.step()
