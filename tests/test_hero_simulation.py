from src.simulation import Simulation
from src.model.dungeon import Dungeon
from src.model.cell import Cell
from src.model.trap import Trap
from src.model.floor import Floor
from src.model.hero import Hero


def make_empty_dungeon(rows=2, cols=2):
    grid = [[Cell((r, c), None) for c in range(cols)] for r in range(rows)]
    return Dungeon((rows, cols), grid, (0, 0), (rows - 1, cols - 1))


def test_add_and_remove_hero_updates_count():
    sim = Simulation()
    h = Hero(10, 10, (0, 0), "none", True)

    sim.add_hero(h)
    assert h in sim.heroes
    assert sim.nb_heroes == 1

    sim.remove_hero(h)
    assert h not in sim.heroes
    assert sim.nb_heroes == 0


def test_apply_cell_effects_reduces_hero_hp_and_marks_dead():
    dungeon = make_empty_dungeon(2, 2)
    trap = Trap(damage=6)
    # place trap at hero location
    dungeon.place_entity(trap, (0, 0))

    h = Hero(12, 12, (0, 0), "none", True)
    sim = Simulation(dungeon=dungeon, heroes=[h])

    # first application: hp reduced but still alive
    sim.apply_cell_effects(h)
    assert h.pv_cur == 6
    assert h.isAlive is True

    # second application: hero dies and hp bottoms at 0
    sim.apply_cell_effects(h)
    assert h.pv_cur == 0
    assert h.isAlive is False


def test_hero_move_and_cell_effects_after_move():
    dungeon = make_empty_dungeon(2, 2)
    trap = Trap(damage=4)
    dungeon.place_entity(trap, (1, 1))

    h = Hero(10, 10, (0, 0), "none", True)
    sim = Simulation(dungeon=dungeon, heroes=[h])

    # move hero to the trap cell and apply effects
    h.move((1, 1))
    sim.apply_cell_effects(h)
    assert h.pv_cur == 6
