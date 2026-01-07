import os, time
from .config import *
from .model.hero import Hero
from .model.waveResult import waveResult
from .model.dungeon import Dungeon
from .model.level import Level
from .observers.Observer import Observer
from .observers.DamageObserver import DamageObserver
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
        level: Level,
        dungeon: Dungeon = None,    
        score: int = 0,
    ) -> None:
        self.dungeon = dungeon
        self.score = int(score)
        self.level = level
        self.heroes = self.level.heroes
        self.current_budget = self.level.budget_tot
        self.ticks = 0
        self.running = False
        self.tresorReached = False
        self.allHeroesDead = False

        self.dmgobserver = DamageObserver()

    def launch(self) -> Dict[str, Any]:
        """Launch the simulation loop.

        Awake a hero every TOURBOUCLE x round
        """
        self.running = True
        count_awake_hero = 0
        while not(self.tresorReached or self.allHeroesDead or not(self.running)):
            if (count_awake_hero <= TOURBOUCLE_REVEIl_HERO * (self.nb_heroes - 1)):
                if count_awake_hero % TOURBOUCLE_REVEIl_HERO == 0:
                    self.heroes[count_awake_hero//TOURBOUCLE_REVEIl_HERO].awake()
                count_awake_hero += 1

            self.step()
            self.ticks += 1
            time.sleep(0.5)
        return waveResult.from_simulation(self).to_dict()

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

        # Let dungeon perform an update if available
        try:
            if self.dungeon and hasattr(self.dungeon, "update"):
                self.dungeon.update(self)
        except Exception:
            pass

        # Let heroes act
        for h in list(self.heroes):
            if h.isAlive :
                try:
                    nextMove = h.getMove()
                    if self.dungeon.validMove(nextMove):
                        h.stepsTaken += 1
                        h.move(nextMove)
                        damage = self.apply_cell_effects(h)
                        self.notifyDamageObserver(damage)
    
                        if self.check_on_treasure(h) :
                            print("Treasure reached!")
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


    def check_on_treasure(self, hero : Hero) -> bool :
        if hero.coord == self.dungeon.treasure_coord :
            self.tresorReached = True
            return True
        return False

    def apply_cell_effects(self, hero: Hero):
        coord = hero.getHero_coord()
        cell = self.dungeon.get_cell(coord)
        hero.take_damage(cell.get_damage())
        return cell.get_damage()

    def notifyDamageObserver(self, dmg : int) :
        self.dmgobserver.update(dmg)

    def score(self) : 
        """
        Fonction de calcul de score
        
        Plus la wave dure longtemps, moins le score sera élevé. Des héros tués rapportent beaucoup de points.
        Le budget dépensé fait office de coefficient
        En moyenne on fera maximum Width*Height ticks pour une wave
        """

        timescore = self.ticks / (WIDTH * HEIGHT)
        killscore = self.level.get_nb_killed_heroes() / self.level.get_nb_heroes() 
        damagescore = self.dmgobserver.getTotalDmg() / self.level.get_sum_HP()
        treasurePenalty = int(self.tresorReached)
        alpha = 0.30
        beta = 0.45
        gamma = 0.25
        eta = 0.9

        score = (alpha * timescore + beta * killscore + gamma * damagescore ) * (1 - eta * treasurePenalty) #entre 0 et 1
        MAX_SCORE = 10000
        return round(score * MAX_SCORE)


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

    

    def __repr__(self) -> str:
        return (
            f"Simulation(level={self.level}, ticks={self.ticks}, score={self.score}, "
            f"heroes={len(self.heroes)}, budget={self.current_budget}/{self.budget_tot})"
        )
