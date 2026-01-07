"""Tests pour la classe Simulation."""

import pytest
from unittest.mock import patch, MagicMock
from src.simulation import Simulation
from src.model.level import Level, LevelBuilder
from src.model.hero import Hero
from src.model.dungeon import Dungeon
from src.model.cell import Cell
from src.model.trap import Trap
from src.model.floor import Floor
from src.model.entity_factory import EntityFactory


def create_test_dungeon(rows=5, cols=5):
    """Helper pour créer un donjon de test."""
    grid = [[Cell((r, c), None) for c in range(cols)] for r in range(rows)]
    return Dungeon(
        dimension=(rows, cols), grid=grid, entry=(0, 0), exit=(rows - 1, cols - 1)
    )


def test_simulation_initialization():
    """Test de l'initialisation basique d'une Simulation."""
    dungeon = create_test_dungeon()
    lvl = (LevelBuilder()
           .set_difficulty(2)
           .set_budget(200)
           .add_hero(pv=100, strategy="random")
           .add_hero(pv=80, strategy="shortest")
           .add_hero(pv=60, strategy="safest")
           .build())
    
    sim = Simulation(level=lvl, dungeon=dungeon)

    assert sim.dungeon is dungeon
    assert sim.level.budget_tot == 200
    assert sim.score == 0
    assert sim.level.difficulty == 2
    assert sim.level.nb_heroes == 3
    assert sim.current_budget == 200
    assert sim.ticks == 0
    assert sim.running is False
    assert sim.tresorReached is False
    assert sim.allHeroesDead is False


def test_simulation_initialization_defaults():
    """Test de l'initialisation avec valeurs par défaut."""
    sim = Simulation(level=Level())

    assert sim.dungeon is None
    assert sim.level.budget_tot == 100
    assert sim.score == 0
    assert sim.level.difficulty == 1
    assert sim.level.nb_heroes == 0
    assert sim.heroes == []
    assert sim.current_budget == 100
    assert sim.ticks == 0


def test_simulation_stop():
    """Test de la méthode stop."""
    sim = Simulation(level=Level())
    sim.running = True

    sim.stop()
    assert sim.running is False


def test_simulation_step():
    """Test de la méthode step."""
    dungeon = create_test_dungeon()
    hero = Hero(pv_total=100, strategy="random", coord=(1, 1))
    hero.path = [(1, 1), (1, 2), (1, 3)]

    lvl = Level(dungeon=dungeon, heroes=[hero], nb_heroes=1)
    sim = Simulation(level=lvl, dungeon=dungeon)
    hero.awake()

    sim.step()

    assert sim.ticks == 1


def test_simulation_step_without_dungeon():
    """Test step sans donjon (ne doit pas crasher)."""
    sim = Simulation(level=Level(dungeon=None, heroes=[], nb_heroes=0))

    sim.step()
    assert sim.ticks == 1


def test_simulation_step_hero_move_valid():
    """Test step avec mouvement valide de héros."""
    dungeon = create_test_dungeon()
    hero = Hero(pv_total=100, strategy="random", coord=(1, 1))
    hero.path = [(1, 1), (1, 2), (1, 3)]

    lvl = Level(dungeon=dungeon, heroes=[hero], nb_heroes=1)
    sim = Simulation(level=lvl, dungeon=dungeon)
    hero.awake()

    sim.step()

    assert hero.coord == (1, 2)
    assert sim.ticks == 1


def test_simulation_step_hero_move_invalid():
    """Test step avec mouvement invalide (hors limites)."""
    dungeon = create_test_dungeon(rows=3, cols=3)
    hero = Hero(pv_total=100, strategy="random", coord=(1, 1))
    hero.path = [(1, 1), (10, 10), (1, 2)]

    lvl = Level(dungeon=dungeon, heroes=[hero], nb_heroes=1)
    sim = Simulation(level=lvl, dungeon=dungeon)
    hero.awake()

    sim.step()

    assert hero.coord == (1, 1)


def test_simulation_step_hero_move_into_wall():
    """Test step avec mouvement vers un mur."""
    dungeon = create_test_dungeon()
    dungeon.place_entity(EntityFactory.create_wall(), (1, 2))

    hero = Hero(pv_total=100, strategy="random", coord=(1, 1))
    hero.path = [(1, 1), (1, 2), (1, 3)]

    lvl = Level(dungeon=dungeon, heroes=[hero], nb_heroes=1)
    sim = Simulation(level=lvl, dungeon=dungeon)
    hero.awake()

    sim.step()

    assert hero.coord == (1, 1)


def test_simulation_step_trap_damage():
    """Test que step applique les dégâts des pièges."""
    dungeon = create_test_dungeon()
    dungeon.place_entity(Trap(damage=15), (1, 2))

    hero = Hero(pv_total=100, strategy="random", coord=(1, 1))
    hero.path = [(1, 1), (1, 2), (1, 3)]

    lvl = Level(dungeon=dungeon, heroes=[hero], nb_heroes=1)
    sim = Simulation(level=lvl, dungeon=dungeon)
    hero.awake()

    sim.step()
    sim.step()

    assert hero.pv_cur == 85
    assert hero.coord == (1, 3)


def test_simulation_add_hero():
    """Test de add_hero."""
    # Use LevelBuilder.add_hero to add heroes to a level, then create Simulation
    from src.model.level import LevelBuilder

    builder = LevelBuilder()
    builder.add_hero(pv=100, strategy="random")
    lvl = builder.build()
    sim = Simulation(level=lvl)

    assert len(sim.heroes) == 1
    assert sim.level.nb_heroes == 1
    assert sim.heroes[0].pv_total == 100

    # add a second hero via the builder and rebuild the level
    builder.add_hero(pv=80, strategy="shortest")
    lvl = builder.build()
    sim = Simulation(level=lvl)

    assert len(sim.heroes) == 2
    assert sim.level.nb_heroes == 2
    assert sim.heroes[1].pv_total == 80


def test_simulation_remove_hero():
    """Test de remove_hero."""
    # Build a level via LevelBuilder with two heroes, then remove one from Simulation
    from src.model.level import LevelBuilder

    builder = LevelBuilder()
    builder.add_hero(pv=100, strategy="random")
    builder.add_hero(pv=80, strategy="shortest")
    lvl = builder.build()
    sim = Simulation(level=lvl)

    hero_to_remove = sim.heroes[0]
    sim.level.remove_hero(hero_to_remove)

    assert len(sim.heroes) == 1
    assert sim.level.nb_heroes == 1


def test_simulation_remove_hero_not_in_list():
    """Test remove_hero quand le héros n'est pas dans la liste."""
    # create a level with one hero via LevelBuilder, then attempt to remove another instance
    from src.model.level import LevelBuilder

    builder = LevelBuilder()
    builder.add_hero(pv=100, strategy="random")
    lvl = builder.build()
    sim = Simulation(level=lvl)

    other = Hero(pv_total=80, strategy="shortest")
    sim.level.remove_hero(other)

    assert len(sim.heroes) == 1
    assert sim.level.nb_heroes == 1


def test_simulation_reset():
    """Test de la méthode reset."""
    dungeon = create_test_dungeon()
    dungeon.place_entity(EntityFactory.create_wall(), (0, 1))

    lvl = Level(dungeon=dungeon, budget_tot=200)
    sim = Simulation(level=lvl, dungeon=dungeon)
    sim.ticks = 10

    sim.reset()

    assert sim.ticks == 0
    assert sim.score == 0
    assert sim.current_budget == 200
    assert sim.running is False
    assert dungeon.is_Walkable((0, 1))


def test_simulation_reset_without_dungeon():
    """Test reset sans donjon."""
    lvl = Level(dungeon=None, budget_tot=100)
    sim = Simulation(level=lvl, dungeon=None)
    sim.ticks = 5

    sim.reset()

    assert sim.ticks == 0
    assert sim.score == 0
    assert sim.current_budget == 100



def test_simulation_repr():
    """Test de la représentation string."""
    sim = Simulation(level=Level(budget_tot=0, nb_heroes=0, heroes=[]))
    sim.ticks = 50

    repr_str = repr(sim)
    assert "Simulation" in repr_str
    assert "level=1" in repr_str
    assert "ticks=50" in repr_str
    assert "score=0" in repr_str
    assert "heroes=0" in repr_str
    assert "budget=0/0" in repr_str


@patch("time.sleep", return_value=None)
def test_simulation_launch_single_step(mock_sleep):
    """Test launch avec un seul step (sans boucle infinie)."""
    dungeon = create_test_dungeon()

    level = (LevelBuilder()
             .set_difficulty(1)
             .set_budget(100)
             .add_hero(pv=100, strategy="random")
             .build())
    hero = level.heroes[0]
    hero.path = [(0, 0), (0, 1)]
    sim = Simulation(level=level, dungeon=dungeon)
    hero.awake()

    original_step = sim.step

    def stop_after_one():
        sim.tresorReached = True
        return original_step()

    sim.step = stop_after_one

    sim.launch()

    assert mock_sleep.called
    assert sim.ticks >= 1


def test_simulation_apply_cell_effects():
    """Test de apply_cell_effects."""
    dungeon = create_test_dungeon()
    dungeon.place_entity(Trap(damage=25), (2, 2))

    hero = Hero(pv_total=100, strategy="random", coord=(2, 2))
    sim = Simulation(level=Level(dungeon=dungeon), dungeon=dungeon)

    sim.apply_cell_effects(hero)

    assert hero.pv_cur == 75


def test_simulation_apply_cell_effects_no_damage():
    """Test apply_cell_effects sur sol (pas de dégâts)."""
    dungeon = create_test_dungeon()

    hero = Hero(pv_total=100, strategy="random", coord=(1, 1))
    sim = Simulation(level=Level(dungeon=dungeon), dungeon=dungeon)

    sim.apply_cell_effects(hero)

    assert hero.pv_cur == 100


def test_simulation_step_hero_dies():
    """Test step quand un héros meurt."""
    dungeon = create_test_dungeon()
    dungeon.place_entity(Trap(damage=100), (1,0))

    lvl = (LevelBuilder()
           .set_difficulty(1)
           .set_budget(100)
           .set_dungeon(dungeon)
           .add_hero(pv=100, strategy="random")
           .build())
    hero = lvl.heroes[0]
    hero.path = [(0, 0), (1, 0)]
    sim = Simulation(level=lvl, dungeon=dungeon)
    hero.awake()

    sim.step()

    assert hero.pv_cur == 0
    assert sim.dmgobserver.getTotalDmg() == 100
    assert hero.isAlive is False


def test_simulation_step_multiple_heroes():
    """Test step avec plusieurs héros."""
    dungeon = create_test_dungeon()

    hero1 = Hero(pv_total=100, strategy="random", coord=(1, 1))
    hero1.path = [(1, 1), (1, 2)]

    hero2 = Hero(pv_total=80, strategy="shortest", coord=(2, 1))
    hero2.path = [(2, 1), (2, 2)]

    lvl = Level(dungeon=dungeon, heroes=[hero1, hero2], nb_heroes=2)
    sim = Simulation(level=lvl, dungeon=dungeon)
    hero1.awake()
    hero2.awake()

    sim.step()

    assert hero1.coord == (1, 2)
    assert hero2.coord == (2, 2)
    assert sim.ticks == 1
