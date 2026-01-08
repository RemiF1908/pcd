from __future__ import annotations
from src.config import *
from .entity import Entity

class Dragon(Entity):
    """Entité représentant un dragon."""

    def __init__(self, orientation : str,damage: int = 30) -> None:
        self._damage = int(damage)
        self.orientation = orientation
        self.current_cooldown = 0
        self.range = []
        self.triggered = False
    @property
    def type(self) -> str:
        return "Dragon"

    @property
    def passable(self) -> bool:
        return True

    @property
    def damage(self) -> int:
        return self._damage

    def update(self, cell) -> None :
        if self.current_cooldown == 0 :
            if self.triggered :
                self.triggered = False
                self.reset_cooldown()
        else : 
            self.decrease_cooldown()

    def init_range(self, coord):
        """Initialise la portée du dragon."""

        row, col = coord
        if self.orientation == "R":
            self.range = [(row, col+i) for i in range(1,WIDTH)]
        if self.orientation == "L":
            self.range = [(row, col-i) for i in range(1,WIDTH)]
        if self.orientation == "U":
            self.range = [(row - i, col) for i in range(1,HEIGHT)]
        if self.orientation == "D":
            self.range = [(row+i, col) for i in range(1,HEIGHT)]

    def getrange(self) -> list[tuple[int, int]]:
        """Retourne la liste des coordonnées dans la portée de l'entité (pour les monstres)."""
        return self.range

    def get_display_char(self) -> str:
        """Retourne 'D' pour représenter un dragon."""
        return "D"

    def get_color_id(self) -> int:
        """Retourne 4 (couleur dragon : rouge)."""
        return 4

    @property
    def max_cooldown(self) -> int:
        return 4

    def __repr__(self) -> str:  
        return f"Dragon(damage={self._damage}, orientation={self.orientation})"