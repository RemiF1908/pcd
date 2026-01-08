from __future__ import annotations

from .entity_creator import EntityCreator
from .bombe import Bombe


class BombeCreator(EntityCreator):
    """Créateur concret pour fabriquer des entités Bombe."""

    def factory_method(self) -> Bombe:
        """Crée et retourne une nouvelle instance de Bombe.

        Returns:
            Instance de Bombe avec damage par défaut à 50.
        """
        return Bombe()
