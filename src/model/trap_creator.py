from __future__ import annotations

from .entity_creator import EntityCreator
from .trap import Trap


class TrapCreator(EntityCreator):
    """Créateur concret pour fabriquer des entités Trap (piège)."""

    def __init__(self, damage: int = 10):
        """Initialise le créateur de piège avec un niveau de dégâts.

        Args:
            damage: Dégâts infligés par le piège (défaut: 10).
        """
        self.damage = damage

    def factory_method(self) -> Trap:
        """Crée et retourne une nouvelle instance de Trap.

        Returns:
            Instance de Trap configurée avec les dégâts spécifiés.
        """
        return Trap(damage=self.damage)
