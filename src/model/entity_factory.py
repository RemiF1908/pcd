"""Factory Facade pour la construction facile des entités du donjon.

Ce module implémente le Design Pattern Factory avec une façade qui utilise
les classes Creator concrètes (FloorCreator, WallCreator, TrapCreator).

Usage:
    from src.model.entity_factory import EntityFactory

    # Créer un sol
    floor = EntityFactory.create_floor()

    # Créer un mur
    wall = EntityFactory.create_wall()

    # Créer un piège
    trap = EntityFactory.create_trap(damage=15)

    # Utilisation directe des créateurs (alternative)
    from src.model.floor_creator import FloorCreator
    floor = FloorCreator().build()
"""

from __future__ import annotations

from .entity import Entity
from .floor import Floor
from .wall import Wall
from .trap import Trap
from .dragon import Dragon
from .bombe import Bombe
from .floor_creator import FloorCreator
from .wall_creator import WallCreator
from .trap_creator import TrapCreator
from .dragon_creator import DragonCreator
from .bombe_creator import BombeCreator


class EntityFactory:
    """Façade centralisée utilisant les classes Creator pour créer les entités."""

    @staticmethod
    def create_floor() -> Floor:
        """Créer une entité Floor (sol marchable).

        Returns:
            Instance de Floor créée via FloorCreator.
        """
        return FloorCreator().factory_method()

    @staticmethod
    def create_wall() -> Wall:
        """Créer une entité Wall (mur non franchissable).

        Returns:
            Instance de Wall créée via WallCreator.
        """
        return WallCreator().factory_method()

    @staticmethod
    def create_trap(damage: int = 10) -> Trap:
        """Créer une entité Trap (piège).

        Args:
            damage: Dégâts infligés par le piège (défaut: 10)

        Returns:
            Instance de Trap créée via TrapCreator.
        """
        return TrapCreator(damage=damage).factory_method()
    
    @staticmethod
    def create_dragon(orientation : str = "U") -> Entity:
        """Créer une entité Dragon (monstre).

        Returns:
            Instance de Dragon créée via DragonCreator.
        """

        return DragonCreator().factory_method(orientation)

    def create_bombe() -> Bombe:
        """Créer une entité Bombe.

        Returns:
            Instance de Bombe créée via BombeCreator.
        """

        return BombeCreator().factory_method()