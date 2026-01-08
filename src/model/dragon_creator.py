from __future__ import annotations

from .entity_creator import EntityCreator
from .dragon import Dragon


class DragonCreator(EntityCreator):
    """Créateur concret pour fabriquer des entités Dragon."""

    def factory_method(self, orientation: str) -> Dragon:
        """Crée et retourne une nouvelle instance de Dragon.

        Args:
            orientation (str): Orientation du dragon ('R', 'L', 'U', 'D').

        Returns:
            Instance de Dragon.
        """
        return Dragon(orientation)
