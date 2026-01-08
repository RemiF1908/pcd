from __future__ import annotations

from .entity import Entity

class Bombe(Entity):
    """Entité représentant une bombe."""

    def __init__(self, damage: int = 50) -> None:
        self._damage = int(damage)
        self.range = []
        self.triggered = False

    @property
    def type(self) -> str:
        return "BOMBE"

    @property
    def cost(self) -> int :
        return 80

    @property
    def passable(self) -> bool:
        return True

    @property
    def damage(self) -> int:
        return self._damage

    def getrange(self) -> list[tuple[int, int]]:
        """Retourne la liste des coordonnées dans la portée de l'entité (pour les monstres)."""
        return self.range

    def init_range(self, coord):
        """Initialise la portée de la bombe (explosion à 1 case autour)."""

        row, col = coord
        self.range = [(row,col), (row+1,col), (row-1,col), (row,col+1), (row,col-1), (row+1,col+1), (row-1,col-1), (row+1,col-1), (row-1,col+1)]

    def update(self, cell) -> None:
        """Met à jour l'état de la bombe (placeholder pour logique future)."""
        if self.triggered :
                cell.remove_monster()
            

    def get_display_char(self) -> str:
        """Retourne 'B' pour représenter une bombe."""
        return "B"

    def get_color_id(self) -> int:
        """Retourne 3 (couleur bombe : rouge)."""
        return 3

    def __repr__(self) -> str:  
        return f"Bombe(damage={self._damage}, )"