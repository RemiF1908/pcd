from .Command import Command


class stopWave(Command):
    """Command to stop a running simulation."""

    def __init__(self, simulation):
        self.simulation = simulation

    def execute(self):
        try:
            self.simulation.stop()
        except Exception:
            print("Failed to stop simulation: invalid object")
