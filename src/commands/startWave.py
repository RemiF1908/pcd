from .Command import Command


class startWave(Command):
    def __init__(self, simulation):
        self.simulation = simulation

    def execute(self, game_controller):
        self.simulation.launch()
