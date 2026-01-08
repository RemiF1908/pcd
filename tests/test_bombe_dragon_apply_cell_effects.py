"""Tests pour les entités Bombe et Dragon via `apply_cell_effects`."""

import pytest

from src.simulation import Simulation
from src.model.dungeon import Dungeon
from src.model.cell import Cell
from src.model.bombe import Bombe
from src.model.dragon import Dragon
from src.model.floor import Floor
from src.model.hero import Hero
from src.model.level import Level


def create_test_dungeon(rows=5, cols=5):
    grid = [[Cell((r, c), None) for c in range(cols)] for r in range(rows)]
    return Dungeon(dimension=(rows, cols), grid=grid, entry=(0, 0), exit=(rows - 1, cols - 1))


def test_bombe_apply_cell_effects():
    dungeon = create_test_dungeon()

    # Place a bombe at (1,2) and initialise sa portée
    bomb = Bombe(damage=40)
    dungeon.place_entity(bomb, (1, 2))

    # Hero se trouve à (1,1) — dans la portée de la bombe
    hero = Hero(pv_total=100, strategy="random", coord=(1, 1))
    hero.awake()
    sim = Simulation(level=Level(dungeon=dungeon), dungeon=dungeon)

    sim.apply_cell_effects(hero)

    assert hero.pv_cur == 60


def test_dragon_apply_cell_effects():
    dungeon = create_test_dungeon()

    # Place a dragon at (2,1) facing right so it can hit (2,3)
    dragon = Dragon(orientation="R", damage=20)
    dungeon.place_entity(dragon, (2, 1))
    # Hero se trouve à (2, 3) — dans la portée du dragon
    hero = Hero(pv_total=100, strategy="random", coord=(2, 3))
    hero.awake()
    hero2 = Hero(pv_total=100, strategy="random", coord=(2, 3))
    hero2.awake()
    sim = Simulation(level=Level(dungeon=dungeon), dungeon=dungeon)

    sim.apply_cell_effects(hero)
    sim.apply_cell_effects(hero2)
    assert hero.pv_cur == 80
    assert hero2.pv_cur == 80
