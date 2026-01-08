from .Command import Command


class resetDungeon(Command):
    """Commande pour réinitialiser le donjon."""

    def __init__(self, dungeon):
        self.dungeon = dungeon

    def execute(self, game_controller) -> None:
        """Exécute la commande de réinitialisation du donjon."""
        self.dungeon.reset()
