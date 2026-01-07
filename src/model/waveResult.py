from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.simulation import Simulation


@dataclass
class waveResult :
    heroesKilled : int
    heroesSurvived : int 
    construction_cost: int
    score: int
    turns: int

    def to_dict(self) -> dict :
        return {
            "heroesKilled" : self.heroesKilled,
            "heroesSurvived" : self.heroesSurvived,
            "construction_cost" : self.construction_cost,
            "score" : self.score,
            "turns" : self.turns
        }
    def getResult(self) -> str :
        return f"Wave Result : {self.to_dict()}"

    @staticmethod
    def getHerosKilled(simulation: 'Simulation') -> int:
        return len([h for h in simulation.heroes if not h.isAlive])

    @staticmethod
    def getHerosSurvived(simulation: 'Simulation') -> int:
        return len([h for h in simulation.heroes if h.isAlive])
    
    @classmethod
    def from_simulation(cls, simulation: 'Simulation') -> 'waveResult':
        heroesKilled = cls.getHerosKilled(simulation)
        heroesSurvived = cls.getHerosSurvived(simulation)
        score = simulation.score
        turns = simulation.ticks
        construction_cost = simulation.level.budget_tot - simulation.current_budget
        return cls(heroesKilled, heroesSurvived, construction_cost, score, turns)
    
    def __repr__(self) -> str :
        return (
            f"waveResult(heroesKilled={self.heroesKilled}, heroesSurvived={self.heroesSurvived}, "
            f"construction_cost={self.construction_cost}, score={self.score}, turns={self.turns})"
        )