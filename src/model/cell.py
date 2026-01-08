from __future__ import annotations

from typing import Optional

from .entity import Entity


class Cell:
    """
    Représente une case du donjon.
    
    Attributes:
        coord : tuple(int, int): Coordonnées (ligne, colonne) de la case
        entity : Abstract class (wall, monster, trap, floor)
    """
    
    # Symboles pour l'affichage terminal

    
    def __init__(self, coord: tuple[int,int], entity: Optional[Entity] = None):   
        """
        Initialise une case avec des coordonnées et une entité.
        """    
        self.coord = coord
        self.entity = entity
    
    @property
    def position(self) -> tuple[int, int]:
        """Retourne la position (row, col)"""
        return (self.coord[0], self.coord[1])
    
    def is_walkable(self) -> bool:
        """Vérifie si un héros peut marcher sur cette case.

        Si `entity` est None, on considère la case comme marchable (floor).
        """
        if self.entity is None:
            return True
        return bool(getattr(self.entity, "passable", True))
    
    def is_dangerous(self) -> bool:
        """Vérifie si la case est dangereuse (piège ou monstre).

        Détermine cela à partir de la valeur `damage` exposée par l'entité.
        """
        if self.entity is None:
            return False
        return getattr(self.entity, "damage", 0) > 0 or getattr(self.entity, "attack_power", 0) > 0
    
    def get_damage(self) -> int:
        """
        Retourne les dégâts infligés par cette case.
        
        Returns:
            Montant de dégâts (0 si case non dangereuse)
        """
        if self.entity is None:
            return 0
        
        return int(getattr(self.entity, "damage", 0) or getattr(self.entity, "attack_power", 0))
    
    def return_damage_if_CD(self) :
        if self.entity.current_cooldown == 0:
            self.entity.reset_cooldown()
            return self.get_damage()
        else:
            self.entity.decrease_cooldown()
            return 0

    def remove_monster(self) -> None:
        """
        Retire le monstre de cette case, en le remplaçant par un floor.
        """
        from .floor_creator import FloorCreator

        if self.entity is not None and getattr(self.entity, "type", None) == "monster":
            self.entity = FloorCreator().build()

    def __repr__(self) -> str:
        ent = getattr(self.entity, "type", None)
        return f"Cell({self.coord[0]}, {self.coord[1]}, {ent})"

