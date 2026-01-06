from .Command import Command

class resetDungeon(Command):
    """Commande pour réinitialiser le donjon."""


    def execute(self, dungeon) -> None:
        """Exécute la commande de réinitialisation du donjon."""
        dungeon.reset()