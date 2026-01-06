from __future__ import annotations

from .entity import Entity


class Floor(Entity):
    """Entité représentant un sol vide (case normale franchissable)."""

    def __init__(self, damage: int = 0):
        self._damage = int(damage)

    @property
    def type(self) -> str:
        return "FLOOR"

    @property
    def passable(self) -> bool:
        return True

    @property
    def damage(self) -> int:
        return 0

    def get_display_char(self) -> str:
        """Retourne '.' pour représenter un sol."""
        return "."

    def get_color_id(self) -> int:
        """Retourne 1 (couleur floor : blanc/gris)."""
        return 1

    def __repr__(self) -> str:  
        return "Floor()"
