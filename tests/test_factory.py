"""Tests pour le Factory Pattern des entités."""

from src.model.entity_factory import EntityFactory
from src.model.floor import Floor
from src.model.wall import Wall
from src.model.trap import Trap
from src.model.cell import Cell


def test_factory_create_floor():
    """Test création d'un Floor via factory."""
    floor = EntityFactory.create_floor()
    assert isinstance(floor, Floor)
    assert floor.type == "FLOOR"
    assert floor.passable is True
    assert floor.damage == 0


def test_factory_create_wall():
    """Test création d'un Wall via factory."""
    wall = EntityFactory.create_wall()
    assert isinstance(wall, Wall)
    assert wall.type == "WALL"
    assert wall.passable is False
    assert wall.damage == 0


def test_factory_create_trap():
    """Test création d'un Trap via factory avec paramètres."""
    trap = EntityFactory.create_trap(damage=15)
    assert isinstance(trap, Trap)
    assert trap.type == "TRAP"
    assert trap.damage == 15
    assert trap.passable is True


def test_factory_trap_default_values():
    """Test création d'un Trap avec valeurs par défaut."""
    trap = EntityFactory.create_trap()
    assert trap.damage == 10


def test_factory_entities_work_with_cell():
    """Test que les entités créées par factory fonctionnent avec Cell."""
    floor = EntityFactory.create_floor()
    wall = EntityFactory.create_wall()
    trap = EntityFactory.create_trap(damage=20)
    
    c_floor = Cell((0, 0), floor)
    assert c_floor.is_walkable()
    assert not c_floor.is_dangerous()
    
    c_wall = Cell((0, 1), wall)
    assert not c_wall.is_walkable()
    
    c_trap = Cell((1, 0), trap)
    assert c_trap.is_walkable()
    assert c_trap.is_dangerous()
    assert c_trap.get_damage() == 20


def test_factory_summary_print():
    """Affichage synthétique et vérifications simples des entités créées."""
    floor = EntityFactory.create_floor()
    wall = EntityFactory.create_wall()
    trap = EntityFactory.create_trap(damage=12)

    assert isinstance(floor, Floor)
    assert isinstance(wall, Wall)
    assert isinstance(trap, Trap)
    assert trap.damage == 12


def test_factory_edge_cases():
    """Cas limites pour Trap: damage 0 et damage très élevé."""
    t0 = EntityFactory.create_trap(damage=0)
    t_big = EntityFactory.create_trap(damage=10**6)
    assert t0.damage == 0
    assert t_big.damage == 10**6
