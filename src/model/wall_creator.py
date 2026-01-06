from __future__ import annotations

from .entity_creator import EntityCreator
from .wall import Wall


class WallCreator(EntityCreator):
    """Créateur concret pour fabriquer des entités Wall (mur non franchissable)."""

    def factory_method(self) -> Wall:
        """Crée et retourne une nouvelle instance de Wall.

        Returns:
            Instance de Wall.
        """
        return Wall()
