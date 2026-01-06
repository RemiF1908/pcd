from __future__ import annotations

from .entity_creator import EntityCreator
from .floor import Floor


class FloorCreator(EntityCreator):
    """Créateur concret pour fabriquer des entités Floor (sol marchable)."""

    def factory_method(self) -> Floor:
        """Crée et retourne une nouvelle instance de Floor.

        Returns:
            Instance de Floor avec damage par défaut à 0.
        """
        return Floor()
