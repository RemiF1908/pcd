from .Command import Command


class startWave(Command):
    def __init__(self, simulation):
        self.simulation = simulation

    def execute(self, game_controller):
        if not(self.simulation.isSimStarted):
            self.simulation.isSimStarted = True
            # for h in self.simulation.heroes:
            #     h.compute_path(simulation.)
        self.simulation.step()
