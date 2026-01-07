from .Command import Command


class stopWave(Command):
    """Command to stop a running simulation."""

    def __init__(self, simulation):
        self.simulation = simulation

    def execute(self, game_controller):
        try:
            self.simulation.stop()
        except Exception:
            print("Failed to stop simulation: invalid object")
