import os
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
        dungeon: Any = None,
        budget_tot: int = 0,
        score: int = 0,
        level: int = 1,
        nb_heroes: int = 0,
        heroes: Optional[List[Any]] = None,
        current_budget: int = 0,
        PathFindingStrategy: Optional[Any] = None,
    ) -> None:
        self.dungeon = dungeon
        self.budget_tot = int(budget_tot)
        self.score = int(score)
        self.level = int(level)
        self.nb_heroes = int(nb_heroes)
        self.heroes = list(heroes) if heroes else []
        self.current_budget = int(current_budget)
        self.pathfinding = PathFindingStrategy
        self.ticks = 0
        self.running = False

    def launch(self, steps: Optional[int] = None) -> Dict[str, Any]:
        """Run the simulation loop.

        If `steps` is provided, run at most that many ticks. Otherwise
        run until `stop_condition()` returns True (by default it stops
        when there are no heroes or budget is exhausted).
        Returns a summary dict when finished.
        """
        self.running = True
        executed = 0
        while self.running:
            if steps is not None and executed >= steps:
                break
            if self.stop_condition():
                break
            self.step()
            executed += 1

        self.running = False
        return self.summary()

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
                if hasattr(h, "act"):
                    h.act(self)
            except Exception:
                # remove hero if it raised irrecoverably and has been flagged
                try:
                    if getattr(h, "dead", False):
                        self.remove_hero(h)
                except Exception:
                    pass

        # Conservative bookkeeping: if dungeon exposes a score or budget
        # aggregator, prefer it. Otherwise little changes are performed
        # here to keep the simulation state consistent.
        try:
            if self.dungeon and hasattr(self.dungeon, "score"):
                self.score = int(getattr(self.dungeon, "score"))
        except Exception:
            pass

        # Decrease budget slightly to simulate costs per tick if budget
        # is present and positive.
        if self.current_budget > 0:
            self.current_budget = max(0, self.current_budget - 1)

    def stop_condition(self) -> bool:
        """Return True when the simulation should stop by default.

        Default: stop when there are no heroes left or current budget
        and total budget are both zero.
        """
        if len(self.heroes) == 0:
            return True
        if self.current_budget <= 0 and self.budget_tot <= 0:
            return True
        return False

    def add_hero(self, hero: Any) -> None:
        self.heroes.append(hero)
        self.nb_heroes = len(self.heroes)

    def remove_hero(self, hero: Any) -> None:
        try:
            self.heroes.remove(hero)
        except ValueError:
            pass
        self.nb_heroes = len(self.heroes)

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


