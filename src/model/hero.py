from typing import List, Optional
from .path_strategies import PathStrategyFactory


class Hero:
    def __init__(self, pv_total, strategy: str, coord=None):
        self.pv_total = pv_total
        self.pv_cur = pv_total
        self.coord = coord
        self.isAlive = False
        self.reachedGoal = False
        self.stepsTaken = 0
        self.path: Optional[List[tuple]] = None
        self.strategy = strategy

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

    
