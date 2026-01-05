from __future__ import annotations

from .entity import Entity


class Wall(Entity):
    """Entité représentant un mur (non franchissable)."""

    def __init__(self) -> None:
        pass

    @property
    def type(self) -> str:
        return "WALL"

    @property
    def passable(self) -> bool:
        return False

    @property
    def damage(self) -> int:
        return 0

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return "Wall()"
