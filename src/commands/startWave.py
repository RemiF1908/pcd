from .Command import Command


class startWave(Command):
    def __init__(self, simulation):
        self.simulation = simulation

    def execute(self):
        self.simulation.launch()
