"""
Module Level avec Builder Pattern pour créer des niveaux de jeu.

Un niveau contient : budget, difficulté, nombre de héros et liste de héros.

Usage:
    from src.model.level import LevelBuilder

    level = (LevelBuilder()
        .set_difficulty(2)
        .set_budget(150)
        .add_hero(pv=100, strategy="safest")
        .add_hero(pv=80, strategy="shortest")
        .build())
"""

from __future__ import annotations
from .dungeon import Dungeon
from typing import List, Optional
from .hero import Hero


class Level:
    """Représente un niveau de jeu.

    Attributes:
        dungeon: Donjon associé au niveau
        budget_tot: Budget total disponible pour ce niveau
        difficulty: Niveau de difficulté (1, 2, 3, ...)
        nb_heroes: Nombre de héros dans ce niveau
        heroes: Liste des héros du niveau
    """

    def __init__(
        self,
        dungeon: Dungeon = None,
        budget_tot: int = 100,
        difficulty: int = 1,
        nb_heroes: int = 0,
        heroes: Optional[List[Hero]] = None,
    ) -> None:
        self.budget_tot = int(budget_tot)
        self.difficulty = int(difficulty)
        self.heroes = list(heroes) if heroes else []
        self.nb_heroes = len(self.heroes)
        self.dungeon = dungeon
        self.entry = self.dungeon.entry if self.dungeon else None
        self.exit = self.dungeon.exit if self.dungeon else None

    @property
    def level(self) -> int:
        """Alias pour difficulty (compatibilité avec Simulation)."""
        return self.difficulty

    def add_hero(self, hero: Hero) -> None:
        """Ajoute un héros au niveau."""
        self.heroes.append(hero)
        self.nb_heroes = len(self.heroes)

    def remove_hero(self, hero: Hero) -> None:
        """Retire un héros du niveau."""
        if hero in self.heroes:
            self.heroes.remove(hero)
            self.nb_heroes = len(self.heroes)

    def awake_hero(self, hero : Hero) : 
        hero.isAlive = True
    
    def get_alive_heroes(self) -> List[Hero]:
        """Retourne la liste des héros encore en vie."""
        return [h for h in self.heroes if h.isAlive]
    
    def get_nb_killed_heroes(self) -> int:
        """Retourne la liste des héros tués."""
        return len([h for h in self.heroes if not h.isAlive])

    def get_nb_heroes(self) -> int :
        return self.nb_heroes

    def get_sum_HP(self) -> int :
        return sum([hero.pv_total for hero in self.heroes])

    def get_hero_positions(self) -> List[tuple]:
        """Retourne les positions de tous les héros vivants."""
        return [h.coord for h in self.heroes if h.isAlive]

    def awake_all_heroes(self) -> None:
        """Réveille tous les héros du niveau."""
        for hero in self.heroes:
            hero.awake()

    def __repr__(self) -> str:
        return (
            f"Level(difficulty={self.difficulty}, budget={self.budget_tot}, "
            f"heroes={self.nb_heroes})"
        )


class LevelBuilder:
    """Builder Pattern pour construire un niveau étape par étape.

    Usage:
        level = (LevelBuilder()
            .set_difficulty(2)
            .set_budget(150)
            .add_hero(pv=100, strategy="random")
            .add_hero(pv=80, strategy="shortest")
            .build())
    """

    def __init__(self) -> None:
        self._budget_tot: int = 100
        self._difficulty: int = 1
        self._nb_heroes: int = 0
        self._heroes: List[Hero] = []
        self._dungeon: Dungeon = None

    def set_dungeon(self, dungeon: Dungeon) -> "LevelBuilder":
        """Définit le donjon associé au niveau."""
        self._dungeon = dungeon
        return self

    def set_budget(self, budget: int) -> "LevelBuilder":
        """Définit le budget total du niveau."""
        self._budget_tot = max(0, int(budget))
        return self

    def set_difficulty(self, difficulty: int) -> "LevelBuilder":
        """Définit la difficulté du niveau."""
        self._difficulty = max(1, int(difficulty))
        return self

    def add_hero(
        self, pv: int = 100, coord: tuple = None, strategy: str = "safest"
    ) -> "LevelBuilder":
        """Ajoute un héros au niveau.

        Args:
            pv: Points de vie totaux et actuels du héros
            strategy: Stratégie de déplacement ("safest", "shortest", etc.)

        Returns:
            self pour le chaînage
        """
        # Hero signature: Hero(pv_total, strategy, coord=None)
        hero = Hero(pv, strategy, coord=coord, hero_number=self._nb_heroes + 1)
        self._heroes.append(hero)
        self._nb_heroes += 1
        return self

    def add_hero_instance(self, hero: Hero) -> "LevelBuilder":
        """Ajoute une instance de Hero existante."""
        self._heroes.append(hero)
        self._nb_heroes += 1
        return self

    def add_heroes(
        self,
        count: int,
        pv: int = 100,
        start_coord: tuple = (0, 0),
        strategy: str = "random",
    ) -> "LevelBuilder":
        """Ajoute plusieurs héros avec les mêmes caractéristiques.

        Args:
            count: Nombre de héros à ajouter
            pv: Points de vie de chaque héros
            start_coord: Position de départ commune
            strategy: Stratégie de déplacement

        Returns:
            self pour le chaînage
        """
        for _ in range(count):
            self.add_hero(pv=pv, coord=start_coord, strategy=strategy)
        return self

    def build(self) -> Level:
        """Construit et retourne le niveau configuré."""
        level = Level(
            budget_tot=self._budget_tot,
            dungeon=self._dungeon,
            difficulty=self._difficulty,
            nb_heroes=len(self._heroes),
            heroes=self._heroes.copy(),
        )

        if self._dungeon:
            from .path_strategies import PathStrategyFactory

            #Met les les héros à la position de l'entrée et calcule leur chemin
            for hero in level.heroes:
                hero.coord = level.entry
                # Only compute path if strategy is supported
                try:
                    PathStrategyFactory.create(hero.strategy)
                    hero.compute_path(self._dungeon, hero.coord, self._dungeon.exit)
                except ValueError:
                    # Strategy not supported (e.g., "random"), skip path computation
                    pass

        return level

    def reset(self) -> "LevelBuilder":
        """Réinitialise le builder pour créer un nouveau niveau."""
        self._budget_tot = 100
        self._difficulty = 1
        self._heroes = []
        self._dungeon = None
        return self

    def __repr__(self) -> str:
        return (
            f"LevelBuilder(difficulty={self._difficulty}, "
            f"budget={self._budget_tot}, heroes={len(self._heroes)})"
        )


class LevelPresets:
    """Niveaux préconfigurés pour démarrer rapidement."""

    @staticmethod
    def easy(dungeon: Dungeon) -> Level:
        """Niveau facile : 1 héros faible, budget élevé."""
        return (
            LevelBuilder()
            .set_difficulty(1)
            .set_budget(200)
            .set_dungeon(dungeon)
            .add_hero(pv=50, coord=dungeon.entry, strategy="random")
            .build()
        )

    @staticmethod
    def medium(dungeon: Dungeon) -> Level:
        """Niveau moyen : 2 héros, budget standard."""
        return (
            LevelBuilder()
            .set_difficulty(2)
            .set_budget(150)
            .set_dungeon(dungeon)
            .add_hero(pv=80, coord=dungeon.entry, strategy="random")
            .build()
        )

    @staticmethod
    def hard(dungeon: Dungeon) -> Level:
        """Niveau difficile : 4 héros forts, budget limité."""
        return (
            LevelBuilder()
            .set_difficulty(3)
            .set_budget(100)
            .set_dungeon(dungeon)
            .add_heroes(count=4, pv=100, start_coord=dungeon.entry, strategy="shortest")
            .build()
        )

    @staticmethod
    def custom(
        difficulty: int,
        budget: int,
        dungeon: Dungeon,
        hero_count: int,
        hero_pv: int = 100,
        strategy: str = "random",
    ) -> Level:
        """Crée un niveau personnalisé rapidement."""
        return (
            LevelBuilder()
            .set_difficulty(difficulty)
            .set_budget(budget)
            .set_dungeon(dungeon)
            .add_heroes(
                count=hero_count,
                pv=hero_pv,
                start_coord=dungeon.entry,
                strategy=strategy,
            )
            .build()
        )
