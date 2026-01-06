"""Tests pour la classe Hero."""

import pytest
from src.model.hero import Hero
from src.model.dungeon import Dungeon
from src.model.cell import Cell
from src.model.floor import Floor
from src.model.trap import Trap
from src.model.wall import Wall
from src.model.entity_factory import EntityFactory


def test_hero_initialization():
    """Test de l'initialisation basique d'un Hero."""
    hero = Hero(pv_total=100, strategy="random")

    assert hero.pv_total == 100
    assert hero.pv_cur == 100
    assert hero.coord is None
    assert hero.isAlive is False
    assert hero.reachedGoal is False
    assert hero.stepsTaken == 0
    assert hero.path is None


def test_hero_initialization_with_coord():
    """Test de l'initialisation avec coordonnées."""
    hero = Hero(pv_total=80, strategy="shortest", coord=(2, 3))

    assert hero.coord == (2, 3)


def test_hero_awake():
    """Test de la méthode awake."""
    hero = Hero(pv_total=100, strategy="random")

    assert hero.isAlive is False

    hero.awake()
    assert hero.isAlive is True


def test_hero_get_hero_coord():
    """Test de getHero_coord."""
    hero = Hero(pv_total=100, strategy="random")

    assert hero.getHero_coord() is None

    hero.coord = (3, 4)
    assert hero.getHero_coord() == (3, 4)


def test_hero_take_damage_partial():
    """Test take_damage - dégâts partiels."""
    hero = Hero(pv_total=100, strategy="random")
    hero.awake()

    hero.take_damage(30)
    assert hero.pv_cur == 70
    assert hero.isAlive is True

    hero.take_damage(20)
    assert hero.pv_cur == 50
    assert hero.isAlive is True


def test_hero_take_damage_lethal():
    """Test take_damage - dégâts mortels."""
    hero = Hero(pv_total=100, strategy="random")

    hero.take_damage(100)
    assert hero.pv_cur == 0
    assert hero.isAlive is False


def test_hero_take_damage_overkill():
    """Test take_damage - dégâts excédant les PV."""
    hero = Hero(pv_total=50, strategy="random")

    hero.take_damage(200)
    assert hero.pv_cur == 0
    assert hero.isAlive is False


def test_hero_take_damage_zero():
    """Test take_damage avec 0 dégâts."""
    hero = Hero(pv_total=100, strategy="random")

    hero.take_damage(0)
    assert hero.pv_cur == 100
    assert hero.isAlive is False


def test_hero_take_damage_multiple():
    """Test plusieurs prises de dégâts."""
    hero = Hero(pv_total=100, strategy="random")

    hero.take_damage(10)
    assert hero.pv_cur == 90

    hero.take_damage(20)
    assert hero.pv_cur == 70

    hero.take_damage(50)
    assert hero.pv_cur == 20

    hero.take_damage(25)
    assert hero.pv_cur == 0
    assert hero.isAlive is False


def test_hero_move():
    """Test de la méthode move."""
    hero = Hero(pv_total=100, strategy="random")

    assert hero.coord is None

    hero.move((1, 1))
    assert hero.coord == (1, 1)

    hero.move((2, 3))
    assert hero.coord == (2, 3)


def test_hero_get_move_with_path():
    """Test getMove avec un chemin défini."""
    hero = Hero(pv_total=100, strategy="random")
    hero.path = [(0, 0), (0, 1), (1, 1), (2, 1), (2, 2)]
    hero.stepsTaken = 0

    move = hero.getMove()
    assert move == (0, 1)

    hero.stepsTaken = 1
    move = hero.getMove()
    assert move == (1, 1)

    hero.stepsTaken = 3
    move = hero.getMove()
    assert move == (2, 2)


def test_hero_get_move_without_path():
    """Test getMove sans chemin (doit lever erreur ou return None)."""
    hero = Hero(pv_total=100, strategy="random")

    with pytest.raises((TypeError, IndexError, AttributeError)):
        hero.getMove()


def test_hero_steps_taken_increment():
    """Test que stepsTaken s'incrémente correctement."""
    hero = Hero(pv_total=100, strategy="random")
    hero.path = [(0, 0), (0, 1), (1, 1)]

    assert hero.stepsTaken == 0

    hero.stepsTaken += 1
    assert hero.stepsTaken == 1

    hero.stepsTaken += 1
    assert hero.stepsTaken == 2


def test_hero_update_with_trap():
    """Test update quand le héros est sur un piège."""
    rows, cols = 3, 3
    grid = [[Cell((r, c), None) for c in range(cols)] for r in range(rows)]
    dungeon = Dungeon(
        dimension=(rows, cols), grid=grid, entry=(0, 0), exit=(rows - 1, cols - 1)
    )

    hero = Hero(pv_total=100, strategy="random", coord=(1, 1))
    hero.awake()
    dungeon.place_entity(Trap(damage=20), (1, 1))

    hero.update(dungeon)
    assert hero.pv_cur == 80
    assert hero.isAlive is True


def test_hero_update_with_floor():
    """Test update quand le héros est sur le sol (pas de dégâts)."""
    rows, cols = 3, 3
    grid = [[Cell((r, c), None) for c in range(cols)] for r in range(rows)]
    dungeon = Dungeon(
        dimension=(rows, cols), grid=grid, entry=(0, 0), exit=(rows - 1, cols - 1)
    )

    hero = Hero(pv_total=100, strategy="random", coord=(1, 1))

    hero.update(dungeon)
    assert hero.pv_cur == 100


def test_hero_death_from_update():
    """Test qu'un héros peut mourir via update()."""
    rows, cols = 3, 3
    grid = [[Cell((r, c), None) for c in range(cols)] for r in range(rows)]
    dungeon = Dungeon(
        dimension=(rows, cols), grid=grid, entry=(0, 0), exit=(rows - 1, cols - 1)
    )

    hero = Hero(pv_total=30, strategy="random", coord=(1, 1))
    hero.awake()
    dungeon.place_entity(Trap(damage=50), (1, 1))

    hero.update(dungeon)
    assert hero.pv_cur == 0
    assert hero.isAlive is False


def test_hero_path_setting():
    """Test qu'on peut définir et utiliser un chemin."""
    hero = Hero(pv_total=100, strategy="random")
    path = [(0, 0), (1, 0), (1, 1), (2, 1)]

    hero.path = path
    assert hero.path == path
    assert len(hero.path) == 4


def test_hero_reached_goal_flag():
    """Test du flag reachedGoal."""
    hero = Hero(pv_total=100, strategy="random")

    assert hero.reachedGoal is False

    hero.reachedGoal = True
    assert hero.reachedGoal is True


def test_hero_different_strategies():
    """Test création de héros avec différentes stratégies."""
    hero1 = Hero(pv_total=100, strategy="random")
    hero2 = Hero(pv_total=80, strategy="shortest")
    hero3 = Hero(pv_total=60, strategy="safest")
    hero4 = Hero(pv_total=120, strategy="custom")

    assert hero1.strategy == "random"
    assert hero2.strategy == "shortest"
    assert hero3.strategy == "safest"
    assert hero4.strategy == "custom"
