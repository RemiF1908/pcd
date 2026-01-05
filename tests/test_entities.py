from src.model.cell import Cell
from src.model.floor import Floor
from src.model.wall import Wall
from src.model.trap import Trap


def test_floor_and_wall_and_trap_behaviour():
    floor = Floor()
    wall = Wall()
    trap = Trap(damage=7)

    c_floor = Cell((0, 0), floor)
    assert c_floor.is_walkable()
    assert not c_floor.is_dangerous()
    assert c_floor.get_damage() == 0

    c_wall = Cell((0, 1), wall)
    assert not c_wall.is_walkable()
    assert not c_wall.is_dangerous()
    assert c_wall.get_damage() == 0

    c_trap = Cell((1, 0), trap)
    assert c_trap.is_walkable()
    assert c_trap.is_dangerous()
    assert c_trap.get_damage() == 7

