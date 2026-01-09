from typing import List, Optional
from src.config import TOURBOUCLE_REVEIl_HERO
from .path_strategies import PathStrategyFactory


class Hero:
    def __init__(self, pv_total, strategy: str, coord=None, hero_number = 1):
        self.pv_total = pv_total
        self.pv_cur = pv_total
        self.coord = coord
        self.isAlive = False
        self.reachedGoal = False
        self.stepsTaken = 0
        self.path: Optional[List[tuple]] = None
        self.strategy = strategy
        self.hero_number = hero_number
        self.ticktoAwake = self.hero_number * TOURBOUCLE_REVEIl_HERO

    def awake(self):
        self.isAlive = True

    def getHero_coord(self):
        return self.coord

    def take_damage(self, damage: int):
        self.pv_cur -= damage
        if self.pv_cur <= 0:
            self.isAlive = False
            self.pv_cur = 0

    def move(self, new_coord: tuple):
        self.coord = new_coord
        self.stepsTaken += 1

    def getMove(self) -> tuple:
        return self.path[self.stepsTaken + 1]

    def update(self, dungeon):
        entity = dungeon.get_cell(self.coord).entity
        self.take_damage(entity.damage)

    def compute_path(self, dungeon, start, goal):
        """Compute path using the assigned strategy."""
        path_strategy = PathStrategyFactory.create(self.strategy)
        self.path = path_strategy.find_path(dungeon, start, goal)

    def reset(self):
        """Reset the hero's state."""
        self.pv_cur = self.pv_total
        self.coord = None
        self.isAlive = False
        self.reachedGoal = False
        self.stepsTaken = 0
        self.path = None
