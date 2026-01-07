from src.model.waveResult import waveResult
from src.model.level import Level
from src.model.hero import Hero
from src.simulation import Simulation


def make_sim_with_heroes(alive_counts=(True, False, True), budget_tot=200, current_budget=150):
    heroes = []
    for is_alive in alive_counts:
        h = Hero(pv_total=10, strategy="none", coord=(0, 0))
        h.isAlive = bool(is_alive)
        heroes.append(h)

    lvl = Level(dungeon=None, budget_tot=budget_tot, heroes=heroes, nb_heroes=len(heroes))
    sim = Simulation(level=lvl, dungeon=None)
    sim.score = 999
    sim.ticks = 42
    sim.current_budget = current_budget
    return sim


def test_waveResult_from_simulation_counts_and_fields():
    sim = make_sim_with_heroes(alive_counts=[True, False, True], budget_tot=200, current_budget=150)

    wr = waveResult.from_simulation(sim)

    assert wr.heroesSurvived == 2
    assert wr.heroesKilled == 1
    assert wr.construction_cost == 50
    assert wr.score == 999
    assert wr.turns == 42


def test_waveResult_to_dict_and_repr_and_helpers():
    sim = make_sim_with_heroes(alive_counts=[False, False], budget_tot=100, current_budget=80)
    # check static helpers directly
    assert waveResult.getHerosKilled(sim) == 2
    assert waveResult.getHerosSurvived(sim) == 0

    wr = waveResult.from_simulation(sim)
    d = wr.to_dict()
    assert isinstance(d, dict)
    assert d["heroesKilled"] == 2
    assert "score" in wr.__repr__()
