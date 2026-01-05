from .Command import Command


class importDungeon(Command):
	"""Command to import a dungeon from a JSON file.

	Minimal implementation: reads the file and returns its contents as a string.
	The caller (controller) should implement actual parsing/creation of Dungeon.
	"""

	def execute(self, filepath: str):
		with open(filepath, 'r') as f:
			data = f.read()
		return data