from dataclasses import dataclass, field

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
