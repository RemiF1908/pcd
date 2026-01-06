"""Tests pour le Level Builder Pattern."""

import pytest
from src.model.level import Level, LevelBuilder
from src.model.hero import Hero


def test_level_creation():
    """Test création basique d'un niveau."""
    level = Level(difficulty=2, budget_tot=150)
    
    assert level.difficulty == 2
    assert level.level == 2  # Alias
    assert level.budget_tot == 150
    assert level.nb_heroes == 0
    assert level.heroes == []


def test_level_add_hero():
    """Test ajout de héros au niveau."""
    level = Level()
    hero = Hero(pv_total=100, strategy="random")
    level.add_hero(hero)
    
    assert level.nb_heroes == 1
    assert level.heroes[0].pv_total == 100


def test_level_builder_basic():
    """Test du builder basique."""
    level = LevelBuilder().build()
    
    assert level.difficulty == 1  # Défaut
    assert level.budget_tot == 100  # Défaut
    assert level.nb_heroes == 0


def test_level_builder_fluent():
    """Test de l'interface fluide du builder."""
    level = (LevelBuilder()
        .set_difficulty(3)
        .set_budget(200)
        .build())
    
    assert level.difficulty == 3
    assert level.budget_tot == 200


def test_level_builder_add_hero():
    """Test ajout de héros via builder."""
    level = (LevelBuilder()
        .set_difficulty(2)
        .add_hero(pv=100, strategy="random")
        .add_hero(pv=60, strategy="shortest")
        .build())
    
    assert level.nb_heroes == 2
    assert level.heroes[0].pv_total == 100
    assert level.heroes[1].pv_total == 60


def test_level_builder_add_heroes_bulk():
    """Test création de plusieurs héros en bloc."""
    level = (LevelBuilder()
        .set_difficulty(1)
        .add_heroes(count=3, pv=80, strategy="random")
        .build())
    
    assert level.nb_heroes == 3
    for hero in level.heroes:
        assert hero.pv_total == 80


def test_level_builder_difficulty_min():
    """Test que la difficulté est au minimum 1."""
    level = LevelBuilder().set_difficulty(0).build()
    
    assert level.difficulty == 1


def test_level_builder_budget_non_negative():
    """Test que le budget ne peut pas être négatif."""
    level = LevelBuilder().set_budget(-50).build()
    
    assert level.budget_tot == 0


def test_level_builder_reset():
    """Test reset du builder."""
    builder = (LevelBuilder()
        .set_difficulty(5)
        .set_budget(500)
        .add_hero(pv=100,strategy="shortest"))
    
    builder.reset()
    level = builder.build()
    
    assert level.difficulty == 1
    assert level.budget_tot == 100
    assert level.nb_heroes == 0


def test_level_builder_add_hero_instance():
    """Test ajout d'une instance Hero existante."""
    hero = Hero(pv_total=150, strategy="custom")
    
    level = (LevelBuilder()
        .add_hero_instance(hero)
        .build())
    
    assert level.nb_heroes == 1
    assert level.heroes[0] is hero


def test_level_get_alive_heroes():
    """Test récupération des héros vivants."""
    level = (LevelBuilder()
        .add_hero(pv=100, strategy="random")
        .add_hero(pv=80, strategy="shortest")
        .build())
    
    # Réveiller les héros
    level.awake_all_heroes()
    
    # Tuer le premier héros
    level.heroes[0].take_damage(200)
    
    alive = level.get_alive_heroes()
    assert len(alive) == 1
    assert alive[0].pv_total == 80


def test_level_remove_hero():
    """Test suppression d'un héros."""
    hero = Hero(pv_total=100, strategy="random")
    level = Level(heroes=[hero])
    
    assert level.nb_heroes == 1
    
    level.remove_hero(hero)
    assert level.nb_heroes == 0


def test_level_repr():
    """Test représentation string."""
    level = (LevelBuilder()
        .set_difficulty(3)
        .set_budget(250)
        .add_hero(pv=100, strategy="safest")
        .build())
    
    repr_str = repr(level)
    assert "difficulty=3" in repr_str
    assert "budget=250" in repr_str
    assert "heroes=1" in repr_str



def test_level_chaining_complete():
    """Test chaînage complet du builder."""
    level = (LevelBuilder()
        .set_difficulty(4)
        .set_budget(300)
        .add_hero(pv=120, strategy="random")
        .add_hero(pv=100, strategy="shortest")
        .add_heroes(count=2, pv=80, strategy="random")
        .build())
    
    assert level.difficulty == 4
    assert level.budget_tot == 300
    assert level.nb_heroes == 4


def test_hero_default_coord_and_move():
    """Vérifie que la coordonnée par défaut est None et que move() la met à jour."""
    hero = Hero(pv_total=42, strategy="random")
    # par défaut, aucune coord n'est assignée
    assert hero.coord is None

    # déplacer le héros
    hero.move((2, 3))
    assert hero.coord == (2, 3)
