"""Factory Pattern pour la construction facile des entités du donjon.

Ce module implémente le Design Pattern Factory pour créer des entités
(Wall, Floor, Trap) de manière simple et centralisée.

Usage:
    from src.model.entity_factory import EntityFactory
    
    # Créer un sol
    floor = EntityFactory.create_floor()
    
    # Créer un mur
    wall = EntityFactory.create_wall()
    
    # Créer un piège
    trap = EntityFactory.create_trap(kind="spike", damage=10)
"""

from __future__ import annotations

from .entity import Entity
from .floor import Floor
from .wall import Wall
from .trap import Trap


class EntityFactory:
    """Factory centralisée pour créer toutes les entités du donjon."""
    
    @staticmethod
    def create_floor(damage: int = 0) -> Floor:
        """Créer une entité Floor (sol marchable).
        
        Args:
            damage: Dégâts infligés en marchant sur ce sol (par défaut 0)
        """
        return Floor(damage=damage)
    
    @staticmethod
    def create_wall() -> Wall:
        """Créer une entité Wall (mur non franchissable)."""
        return Wall()
    
    @staticmethod
    def create_trap(damage: int = 10) -> Trap:
        """Créer une entité Trap (piège).

        Args:
            damage: Dégâts infligés par le piège

        Returns:
            Instance de Trap configurée
        """
        return Trap(damage=damage)
