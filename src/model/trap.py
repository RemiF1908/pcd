from __future__ import annotations

from .entity import Entity


class Trap(Entity):
    """Entité représentant un piège posé sur une case.

    Attributes:
        damage: int -- dégâts infligés lorsqu'un héros déclenche le piège
    """

    def __init__(self, damage: int = 10):
        self._damage = int(damage)

    @property
    def type(self) -> str:
        return "TRAP"

    @property
    def cost(self) -> int :
        return 30

    @property
    def passable(self) -> bool:
        # Un piège est placé sur une case franchissable (on peut marcher dessus)
        return True

    @property
    def damage(self) -> int:
        return self._damage

    def update(self, cell) -> None:
        """Met à jour l'état du piège (placeholder pour logique future)."""
        pass   

    def get_display_char(self) -> str:
        return "^"

    def get_color_id(self) -> int:
        return 3  # Rouge pour les pièges (paire curses 3)

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"Trap(damage={self._damage})"
