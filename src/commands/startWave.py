from .Command import Command

class startWave(Command) :
    def execute(self, simulation):
        print("Wave started")
        simulation.launch()
