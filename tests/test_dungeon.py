"""Tests pour la classe Dungeon."""

import pytest
from src.model.dungeon import Dungeon
from src.model.cell import Cell
from src.model.floor import Floor
from src.model.wall import Wall
from src.model.trap import Trap
from src.model.entity_factory import EntityFactory


def test_dungeon_initialization():
    """Test de l'initialisation basique d'un Dungeon."""
    rows, cols = 5, 8
    grid = [[Cell((r, c), None) for c in range(cols)] for r in range(rows)]
    dungeon = Dungeon(
        dimension=(rows, cols), grid=grid, entry=(0, 0), exit=(rows - 1, cols - 1)
    )

    assert dungeon.dimension == (rows, cols)
    assert dungeon.entry == (0, 0)
    assert dungeon.exit == (rows - 1, cols - 1)
    assert len(dungeon.grid) == rows
    assert len(dungeon.grid[0]) == cols


def test_dungeon_fills_with_floor():
    """Test que le constructeur remplit toutes les cellules avec Floor."""
    rows, cols = 3, 4
    grid = [[Cell((r, c), None) for c in range(cols)] for r in range(rows)]
    dungeon = Dungeon(
        dimension=(rows, cols), grid=grid, entry=(0, 0), exit=(rows - 1, cols - 1)
    )

    for row in dungeon.grid:
        for cell in row:
            assert isinstance(cell.entity, Floor)


def test_dungeon_get_cell():
    """Test de la méthode get_cell."""
    rows, cols = 4, 5
    grid = [[Cell((r, c), None) for c in range(cols)] for r in range(rows)]
    dungeon = Dungeon(
        dimension=(rows, cols), grid=grid, entry=(0, 0), exit=(rows - 1, cols - 1)
    )

    cell = dungeon.get_cell((1, 2))
    assert cell.coord == (1, 2)
    assert isinstance(cell.entity, Floor)


def test_dungeon_is_within_bounds():
    """Test de la méthode is_within_bounds."""
    rows, cols = 5, 6
    grid = [[Cell((r, c), None) for c in range(cols)] for r in range(rows)]
    dungeon = Dungeon(
        dimension=(rows, cols), grid=grid, entry=(0, 0), exit=(rows - 1, cols - 1)
    )

    assert dungeon.is_within_bounds((0, 0))
    assert dungeon.is_within_bounds((rows - 1, cols - 1))
    assert dungeon.is_within_bounds((2, 3))
    assert not dungeon.is_within_bounds((-1, 0))
    assert not dungeon.is_within_bounds((0, -1))
    assert not dungeon.is_within_bounds((rows, 0))
    assert not dungeon.is_within_bounds((0, cols))


def test_dungeon_is_walkable():
    """Test de la méthode is_Walkable."""
    rows, cols = 3, 4
    grid = [[Cell((r, c), None) for c in range(cols)] for r in range(rows)]
    dungeon = Dungeon(
        dimension=(rows, cols), grid=grid, entry=(0, 0), exit=(rows - 1, cols - 1)
    )

    assert dungeon.is_Walkable((0, 0))
    assert dungeon.is_Walkable((1, 1))

    dungeon.place_entity(EntityFactory.create_wall(), (1, 1))
    assert not dungeon.is_Walkable((1, 1))


def test_dungeon_valid_move():
    """Test de la méthode validMove."""
    rows, cols = 3, 4
    grid = [[Cell((r, c), None) for c in range(cols)] for r in range(rows)]
    dungeon = Dungeon(
        dimension=(rows, cols), grid=grid, entry=(0, 0), exit=(rows - 1, cols - 1)
    )

    assert dungeon.validMove((0, 0))
    assert dungeon.validMove((1, 1))

    assert not dungeon.validMove((-1, 0))
    assert not dungeon.validMove((0, cols))

    dungeon.place_entity(EntityFactory.create_wall(), (1, 1))
    assert not dungeon.validMove((1, 1))


def test_dungeon_place_entity():
    """Test de la méthode place_entity."""
    rows, cols = 3, 3
    grid = [[Cell((r, c), None) for c in range(cols)] for r in range(rows)]
    dungeon = Dungeon(
        dimension=(rows, cols), grid=grid, entry=(0, 0), exit=(rows - 1, cols - 1)
    )

    wall = EntityFactory.create_wall()
    dungeon.place_entity(wall, (1, 1))

    cell = dungeon.get_cell((1, 1))
    assert cell.entity is wall


def test_dungeon_place_entity_out_of_bounds():
    """Test place_entity avec coordonnées hors limites (doit ignorer)."""
    rows, cols = 3, 3
    grid = [[Cell((r, c), None) for c in range(cols)] for r in range(rows)]
    dungeon = Dungeon(
        dimension=(rows, cols), grid=grid, entry=(0, 0), exit=(rows - 1, cols - 1)
    )

    wall = EntityFactory.create_wall()
    dungeon.place_entity(wall, (-1, 0))
    dungeon.place_entity(wall, (10, 10))

    assert dungeon.is_Walkable((0, 0))


def test_dungeon_reset():
    """Test de la méthode reset."""
    rows, cols = 3, 3
    grid = [[Cell((r, c), None) for c in range(cols)] for r in range(rows)]
    dungeon = Dungeon(
        dimension=(rows, cols), grid=grid, entry=(0, 0), exit=(rows - 1, cols - 1)
    )

    dungeon.place_entity(EntityFactory.create_wall(), (0, 1))
    dungeon.place_entity(EntityFactory.create_trap(damage=10), (1, 1))

    assert not dungeon.is_Walkable((0, 1))
    assert dungeon.get_cell((1, 1)).is_dangerous()

    dungeon.reset()

    assert dungeon.is_Walkable((0, 1))
    assert not dungeon.get_cell((1, 1)).is_dangerous()
    for row in dungeon.grid:
        for cell in row:
            assert isinstance(cell.entity, Floor)


def test_dungeon_repr():
    """Test de la représentation string."""
    rows, cols = 4, 5
    grid = [[Cell((r, c), None) for c in range(cols)] for r in range(rows)]
    dungeon = Dungeon(
        dimension=(rows, cols), grid=grid, entry=(0, 0), exit=(rows - 1, cols - 1)
    )

    repr_str = repr(dungeon)
    assert "Dungeon" in repr_str
    assert f"dimension=({rows}, {cols})" in repr_str
    assert "entry=(0, 0)" in repr_str
    assert f"exit=({rows - 1}, {cols - 1})" in repr_str


def test_dungeon_trap_still_walkable():
    """Test qu'un piège reste marchable (les héros peuvent y passer)."""
    rows, cols = 3, 3
    grid = [[Cell((r, c), None) for c in range(cols)] for r in range(rows)]
    dungeon = Dungeon(
        dimension=(rows, cols), grid=grid, entry=(0, 0), exit=(rows - 1, cols - 1)
    )

    dungeon.place_entity(EntityFactory.create_trap(damage=15), (1, 1))

    assert dungeon.is_Walkable((1, 1))
    assert dungeon.get_cell((1, 1)).is_dangerous()


def test_dungeon_multiple_entities_placement():
    """Test placement multiple d'entités de différents types."""
    rows, cols = 4, 4
    grid = [[Cell((r, c), None) for c in range(cols)] for r in range(rows)]
    dungeon = Dungeon(
        dimension=(rows, cols), grid=grid, entry=(0, 0), exit=(rows - 1, cols - 1)
    )

    dungeon.place_entity(EntityFactory.create_wall(), (0, 1))
    dungeon.place_entity(EntityFactory.create_trap(damage=5), (1, 0))
    dungeon.place_entity(EntityFactory.create_trap(damage=20), (2, 2))

    assert not dungeon.is_Walkable((0, 1))
    assert dungeon.is_Walkable((1, 0))
    assert dungeon.is_Walkable((2, 2))

    assert dungeon.get_cell((1, 0)).get_damage() == 5
    assert dungeon.get_cell((2, 2)).get_damage() == 20
