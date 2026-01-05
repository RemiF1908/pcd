from .Command import Command


class stopWave(Command):
	"""Command to stop a running simulation."""

	def execute(self, simulation):
		try:
			simulation.running = False
			print("Wave stopped")
		except Exception:
			print("Failed to stop simulation: invalid object")

