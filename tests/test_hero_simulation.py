from src.simulation import Simulation
from src.model.level import Level
from src.model.dungeon import Dungeon
from src.model.cell import Cell
from src.model.trap import Trap
from src.model.floor import Floor
from src.model.hero import Hero


def make_empty_dungeon(rows=2, cols=2):
    grid = [[Cell((r, c), None) for c in range(cols)] for r in range(rows)]
    return Dungeon((rows, cols), grid, (0, 0), (rows - 1, cols - 1))


def test_add_and_remove_hero_updates_count():
    sim = Simulation(level=Level())
    h = Hero(pv_total=10, strategy="none", coord=(0, 0))
    h.awake()

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

    h = Hero(pv_total=12, strategy="none", coord=(0, 0))
    h.awake()
    lvl = Level(dungeon=dungeon, heroes=[h])
    sim = Simulation(level=lvl, dungeon=dungeon)

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

    h = Hero(pv_total=10, strategy="none", coord=(0, 0))
    h.awake()
    lvl = Level(dungeon=dungeon, heroes=[h])
    sim = Simulation(level=lvl, dungeon=dungeon)

    # move hero to the trap cell and apply effects
    h.move((1, 1))
    sim.apply_cell_effects(h)
    assert h.pv_cur == 6
