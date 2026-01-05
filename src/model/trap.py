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
    def passable(self) -> bool:
        # Un piège est placé sur une case franchissable (on peut marcher dessus)
        return True

    @property
    def damage(self) -> int:
        return self._damage

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"Trap(damage={self._damage})"
