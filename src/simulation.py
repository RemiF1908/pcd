import os, time
import VARIABLES as VAR
from model.hero import Hero
from model.dungeon import Dungeon
from typing import List, Optional, Any, Dict

# Use the project package path so imports work when running tests and
# modules from the repository: the dungeon module lives under `src.model`.
from src.model import dungeon as dgeon


class Simulation:
    """Lightweight simulation orchestrator.

    This class provides a small, pragmatic API to run a simulation loop
    that delegates behaviour to a `dungeon` and its `heroes` when those
    objects expose expected methods. The implementation is defensive so
    it works even if `model.dungeon` or `hero` modules are minimal or
    incomplete in the current workspace.
    """

    def __init__(
        self,
        dungeon: Dungeon = None,
        budget_tot: int = 0,
        score: int = 0,
        level: int = 1,
        nb_heroes: int = 0,
        heroes: Optional[List[Hero]] = None,
        current_budget: int = 0,

    ) -> None:
        self.dungeon = dungeon
        self.budget_tot = int(budget_tot)
        self.score = int(score)
        self.level = int(level)
        self.nb_heroes = int(nb_heroes)
        self.heroes = list(heroes) if heroes else []
        self.current_budget = int(current_budget)
        self.ticks = 0
        self.running = False
        self.tresorReached = False
        self.allHeroesDead = False

    def launch(self) -> Dict[str, Any]:
        """Run the simulation loop.

        If `steps` is provided, run at most that many ticks. Otherwise
        run until `stop_condition()` returns True (by default it stops
        when there are no heroes or budget is exhausted).
        Returns a summary dict when finished.
        """
        self.running = True
        count_awake_hero = 0
        while not(self.tresorReached or self.allHeroesDead or not(self.running)):
            if (count_awake_hero <= VAR.TOURBOUCLE_REVEIl_HERO * (self.nb_heroes - 1)):
                if count_awake_hero % VAR.TOURBOUCLE_REVEIl_HERO == 0:
                    self.heroes[count_awake_hero//VAR.TOURBOUCLE_REVEIl_HERO].awake()
                count_awake_hero += 1

            self.step()
            time.sleep(0.5)
            
    def stop(self) -> None:
        """Stop the simulation loop."""
        self.running = False

    def step(self) -> None:
        """Advance the simulation by one tick.

        This method attempts to call common hooks on `dungeon` and on each
        hero (`update`, `act`), but will silently continue if those
        attributes are not present. It increments `ticks` and may adjust
        `score` or `current_budget` if the provided objects expose the
        corresponding information.
        """
        self.ticks += 1

        # Let dungeon perform an update if available
        try:
            if self.dungeon and hasattr(self.dungeon, "update"):
                self.dungeon.update(self)
        except Exception:
            pass

        # Let heroes act
        for h in list(self.heroes):
            try:
                nextMove = h.getMove()
                if self.dungeon.validMove(nextMove) :
                    h.move(nextMove)
                    self.apply_cell_effects(h)
            except Exception:
                print("illegal move")

        # Conservative bookkeeping: if dungeon exposes a score or budget
        # aggregator, prefer it. Otherwise little changes are performed
        # here to keep the simulation state consistent.
        try:
            if self.dungeon and hasattr(self.dungeon, "score"):
                self.score = int(getattr(self.dungeon, "score"))
        except Exception:
            pass



    def add_hero(self, hero: Any) -> None:
        self.heroes.append(hero)
        self.nb_heroes = len(self.heroes)

    def remove_hero(self, hero: Any) -> None:
        try:
            self.heroes.remove(hero)
        except ValueError:
            pass
        self.nb_heroes = len(self.heroes)

    def apply_cell_effects(self, hero : Hero) :
        coord = hero.getHero_coord()
        cell = self.dungeon.get_cell(coord)
        hero.take_damage(cell.get_damage())
        

    def reset(self) -> None:
        self.ticks = 0
        self.score = 0
        self.current_budget = self.budget_tot
        self.running = False
        try:
            if self.dungeon and hasattr(self.dungeon, "reset"):
                self.dungeon.reset()
        except Exception:
            pass

    def summary(self) -> Dict[str, Any]:
        return {
            "ticks": self.ticks,
            "score": self.score,
            "level": self.level,
            "nb_heroes": self.nb_heroes,
            "current_budget": self.current_budget,
        }

    def __repr__(self) -> str:
        return (
            f"Simulation(level={self.level}, ticks={self.ticks}, score={self.score}, "
            f"heroes={len(self.heroes)}, budget={self.current_budget}/{self.budget_tot})"
        )


