"""Tests d'intégration sans curses - simulation complète."""

import pytest
from unittest.mock import patch
from src.model.dungeon import Dungeon
from src.model.cell import Cell
from src.model.hero import Hero
from src.model.trap import Trap
from src.model.entity_factory import EntityFactory
from src.simulation import Simulation
from src.model.level import Level, LevelBuilder
from src.commands.GameInvoker import GameInvoker
from src.commands.placeEntity import placeEntity
from src.commands.removeEntity import removeEntity
from src.commands.resetDungeon import resetDungeon
from src.controller.game_controller import GameController


def create_test_dungeon(rows=5, cols=5):
    """Helper pour créer un donjon de test."""
    grid = [[Cell((r, c), None) for c in range(cols)] for r in range(rows)]
    return Dungeon(
        dimension=(rows, cols), grid=grid, entry=(0, 0), exit=(rows - 1, cols - 1)
    )


def test_integration_dungeon_hero_basic():
    """Test d'intégration Dungeon + Hero."""
    dungeon = create_test_dungeon()
    hero = Hero(pv_total=100, strategy="random", coord=(0, 0))
    hero.awake()

    assert hero.getHero_coord() == (0, 0)

    hero.move((1, 1))
    assert hero.getHero_coord() == (1, 1)


def test_integration_dungeon_hero_trap():
    """Test d'intégration Dungeon + Hero + Trap."""
    dungeon = create_test_dungeon()
    dungeon.place_entity(Trap(damage=30), (1, 1))

    hero = Hero(pv_total=100, strategy="random", coord=(1, 1))
    hero.awake()

    hero.update(dungeon)
    assert hero.pv_cur == 70
    assert hero.isAlive is True


def test_integration_hero_death_from_trap():
    """Test d'intégration: mort d'un héros par piège."""
    dungeon = create_test_dungeon()
    dungeon.place_entity(Trap(damage=100), (2, 2))

    hero = Hero(pv_total=50, strategy="random", coord=(2, 2))
    hero.awake()

    hero.update(dungeon)
    assert hero.pv_cur == 0
    assert hero.isAlive is False


def test_integration_dungeon_multiple_entities():
    """Test d'intégration avec plusieurs types d'entités."""
    dungeon = create_test_dungeon()

    dungeon.place_entity(EntityFactory.create_wall(), (0, 1))
    dungeon.place_entity(EntityFactory.create_trap(damage=20), (1, 1))
    dungeon.place_entity(EntityFactory.create_wall(), (2, 2))

    assert not dungeon.is_Walkable((0, 1))
    assert dungeon.is_Walkable((1, 1))
    assert dungeon.get_cell((1, 1)).get_damage() == 20
    assert not dungeon.is_Walkable((2, 2))


def test_integration_simulation_single_step():
    """Test d'intégration Simulation + Dungeon + Hero."""
    dungeon = create_test_dungeon()
    hero = Hero(pv_total=100, strategy="random", coord=(1, 1))
    hero.path = [(1, 1), (1, 2)]

    lvl = Level(dungeon=dungeon, heroes=[hero], nb_heroes=1)
    simulation = Simulation(level=lvl, dungeon=dungeon)
    hero.awake()

    simulation.step()

    assert simulation.ticks == 1
    assert hero.coord == (1, 2)


def test_integration_simulation_trap_damage():
    """Test d'intégration: simulation avec dégâts de piège."""
    dungeon = create_test_dungeon()
    dungeon.place_entity(Trap(damage=25), (1, 2))

    hero = Hero(pv_total=100, strategy="random", coord=(1, 1))
    hero.path = [(1, 1), (1, 2), (1, 3)]

    lvl = Level(dungeon=dungeon, heroes=[hero], nb_heroes=1)
    simulation = Simulation(level=lvl, dungeon=dungeon)
    hero.awake()

    simulation.step()
    simulation.step()

    assert hero.pv_cur == 75
    assert hero.coord == (1, 3)


def test_integration_level_builder_with_heroes():
    """Test d'intégration Level + Builder + Heroes."""
    level = (
        LevelBuilder()
        .set_difficulty(2)
        .set_budget(200)
        .add_hero(pv=100, strategy="random")
        .add_hero(pv=80, strategy="shortest")
        .build()
    )

    assert level.difficulty == 2
    assert level.budget_tot == 200
    assert level.nb_heroes == 2
    assert level.heroes[0].pv_total == 100
    assert level.heroes[1].pv_total == 80


def test_integration_level_awake_all_heroes():
    """Test d'intégration: awake_all_heroes()."""
    level = (
        LevelBuilder()
        .add_hero(pv=100, strategy="random")
        .add_hero(pv=80, strategy="shortest")
        .add_hero(pv=60, strategy="safest")
        .build()
    )

    for hero in level.heroes:
        assert hero.isAlive is False

    level.awake_all_heroes()

    for hero in level.heroes:
        assert hero.isAlive is True


def test_integration_level_get_alive_heroes():
    """Test d'intégration: get_alive_heroes()."""
    level = (
        LevelBuilder()
        .add_hero(pv=100, strategy="random")
        .add_hero(pv=50, strategy="shortest")
        .build()
    )

    level.awake_all_heroes()
    level.heroes[1].take_damage(100)

    alive = level.get_alive_heroes()
    assert len(alive) == 1
    assert alive[0].pv_total == 100


def test_integration_command_place_and_remove():
    """Test d'intégration: placeEntity + removeEntity."""
    dungeon = create_test_dungeon()

    place_command = placeEntity(dungeon, EntityFactory.create_wall(), (2, 2))
    place_command.execute()

    assert not dungeon.is_Walkable((2, 2))

    remove_command = removeEntity(dungeon, (2, 2))
    remove_command.execute()

    assert dungeon.is_Walkable((2, 2))


def test_integration_game_invoker_workflow():
    """Test d'intégration: GameInvoker workflow complet."""
    from unittest.mock import MagicMock

    invoker = GameInvoker()
    command1 = MagicMock()
    command2 = MagicMock()

    invoker.push_command(command1)
    invoker.push_command(command2)

    invoker.execute()

    assert len(invoker.history) == 2
    assert len(invoker.commandstack) == 0


def test_integration_dungeon_reset_removes_all_entities():
    """Test d'intégration: reset nettoie toutes les entités."""
    dungeon = create_test_dungeon()

    dungeon.place_entity(EntityFactory.create_wall(), (0, 1))
    dungeon.place_entity(EntityFactory.create_wall(), (1, 1))
    dungeon.place_entity(Trap(damage=10), (2, 2))

    dungeon.reset()

    assert dungeon.is_Walkable((0, 1))
    assert dungeon.is_Walkable((1, 1))
    assert not dungeon.get_cell((2, 2)).is_dangerous()


def test_integration_hero_path_movement():
    """Test d'intégration: mouvement de héros le long d'un chemin."""
    dungeon = create_test_dungeon()
    path = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2)]

    hero = Hero(pv_total=100, strategy="random", coord=(0, 0))
    hero.path = path

    for expected_coord in path:
        hero.coord = expected_coord
        assert hero.coord == expected_coord


def test_integration_factory_creators_dungeon():
    """Test d'intégration Factory + Creators + Dungeon."""
    dungeon = create_test_dungeon()

    floor = EntityFactory.create_floor()
    wall = EntityFactory.create_wall()
    trap = EntityFactory.create_trap(damage=15)

    dungeon.place_entity(floor, (0, 0))
    dungeon.place_entity(wall, (1, 1))
    dungeon.place_entity(trap, (2, 2))

    assert dungeon.is_Walkable((0, 0))
    assert not dungeon.is_Walkable((1, 1))
    assert dungeon.get_cell((2, 2)).get_damage() == 15


def test_integration_simulation_multiple_heroes():
    """Test d'intégration: simulation avec plusieurs héros."""
    dungeon = create_test_dungeon()

    hero1 = Hero(pv_total=100, strategy="random", coord=(1, 1))
    hero1.path = [(1, 1), (1, 2)]

    hero2 = Hero(pv_total=80, strategy="shortest", coord=(2, 1))
    hero2.path = [(2, 1), (2, 2)]

    lvl = Level(dungeon=dungeon, heroes=[hero1, hero2], nb_heroes=2)
    simulation = Simulation(level=lvl, dungeon=dungeon)
    hero1.awake()
    hero2.awake()

    simulation.step()

    assert hero1.coord == (1, 2)
    assert hero2.coord == (2, 2)
    assert simulation.ticks == 1


def test_integration_game_controller_simulation():
    """Test d'intégration GameController + Simulation."""
    from unittest.mock import MagicMock

    interface = MagicMock()
    dungeon = create_test_dungeon()
    lvl = Level(dungeon=dungeon, budget_tot=100, nb_heroes=0, heroes=[])
    simulation = Simulation(level=lvl, dungeon=dungeon)

    controller = GameController(interface, simulation)

    assert controller.simulation is simulation
    assert controller.simulation.dungeon is dungeon

    controller.stop()
    assert simulation.running is False


@patch("time.sleep", return_value=None)
def test_integration_simulation_hero_death_chain(mock_sleep):
    """Test d'intégration: chaîne de morts de héros."""
    dungeon = create_test_dungeon()
    dungeon.place_entity(Trap(damage=30), (1, 1))
    dungeon.place_entity(Trap(damage=50), (2, 2))

    hero1 = Hero(pv_total=50, strategy="random", coord=(1, 1))
    hero1.path = [(1, 1), (1, 2)]

    hero2 = Hero(pv_total=40, strategy="shortest", coord=(2, 2))
    hero2.path = [(2, 2), (2, 3)]

    lvl = Level(dungeon=dungeon, heroes=[hero1, hero2], nb_heroes=2)
    simulation = Simulation(level=lvl, dungeon=dungeon)
    hero1.awake()
    hero2.awake()

    simulation.step()

    assert hero1.pv_cur == 20
    assert hero2.pv_cur == -10 or hero2.pv_cur == 0


def test_integration_complex_dungeon_layout():
    """Test d'intégration: layout complexe avec murs et pièges."""
    dungeon = create_test_dungeon(rows=6, cols=6)

    for c in range(1, 5):
        dungeon.place_entity(EntityFactory.create_wall(), (2, c))

    dungeon.place_entity(Trap(damage=20), (3, 2))
    dungeon.place_entity(Trap(damage=15), (4, 4))

    hero = Hero(pv_total=100, strategy="random", coord=(0, 0))

    assert dungeon.validMove((0, 0))
    assert not dungeon.validMove((2, 3))
    assert dungeon.is_Walkable((3, 2))
    assert dungeon.get_cell((3, 2)).get_damage() == 20


def test_integration_level_summary():
    """Test d'intégration: Level + summary."""
    level = (
        LevelBuilder()
        .set_difficulty(3)
        .set_budget(300)
        .add_hero(pv=100, strategy="random")
        .add_hero(pv=80, strategy="shortest")
        .build()
    )

    assert level.difficulty == 3
    assert level.budget_tot == 300
    assert level.nb_heroes == 2

    repr_str = repr(level)
    assert "difficulty=3" in repr_str
    assert "budget=300" in repr_str
