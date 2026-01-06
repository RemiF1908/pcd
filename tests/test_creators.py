"""Tests pour les classes Creator du Pattern Factory."""

from src.model.entity_creator import EntityCreator
from src.model.floor_creator import FloorCreator
from src.model.wall_creator import WallCreator
from src.model.trap_creator import TrapCreator
from src.model.entity import Entity
from src.model.floor import Floor
from src.model.wall import Wall
from src.model.trap import Trap


def test_floor_creator_returns_floor():
    """Test que FloorCreator crée bien une instance de Floor."""
    creator = FloorCreator()
    floor = creator.build()

    assert isinstance(floor, Floor)
    assert isinstance(floor, Entity)
    assert floor.type == "FLOOR"
    assert floor.passable is True
    assert floor.damage == 0


def test_wall_creator_returns_wall():
    """Test que WallCreator crée bien une instance de Wall."""
    creator = WallCreator()
    wall = creator.build()

    assert isinstance(wall, Wall)
    assert isinstance(wall, Entity)
    assert wall.type == "WALL"
    assert wall.passable is False
    assert wall.damage == 0


def test_trap_creator_default_damage():
    """Test que TrapCreator crée une instance de Trap avec dégâts par défaut."""
    creator = TrapCreator()
    trap = creator.build()

    assert isinstance(trap, Trap)
    assert isinstance(trap, Entity)
    assert trap.type == "TRAP"
    assert trap.passable is True
    assert trap.damage == 10


def test_trap_creator_custom_damage():
    """Test que TrapCreator crée une instance de Trap avec dégâts personnalisés."""
    creator = TrapCreator(damage=25)
    trap = creator.build()

    assert isinstance(trap, Trap)
    assert trap.damage == 25


def test_creators_are_entity_creators():
    """Test que tous les créateurs héritent bien de EntityCreator."""
    floor_creator = FloorCreator()
    wall_creator = WallCreator()
    trap_creator = TrapCreator()

    assert isinstance(floor_creator, EntityCreator)
    assert isinstance(wall_creator, EntityCreator)
    assert isinstance(trap_creator, EntityCreator)


def test_trap_creator_edge_cases():
    """Test des cas limites pour TrapCreator."""
    trap_zero = TrapCreator(damage=0).build()
    assert trap_zero.damage == 0

    trap_big = TrapCreator(damage=1000).build()
    assert trap_big.damage == 1000

    trap_negative = TrapCreator(damage=-5).build()
    assert trap_negative.damage == -5


def test_creators_multiple_instances():
    """Test que chaque appel à build() crée une nouvelle instance."""
    creator = FloorCreator()

    floor1 = creator.build()
    floor2 = creator.build()

    assert floor1 is not floor2
    assert floor1.type == floor2.type
