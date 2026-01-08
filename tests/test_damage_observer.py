from src.observers.DamageObserver import DamageObserver


def test_damage_observer_accumulates_and_records_lastdamage(capsys):
    obs = DamageObserver()
    assert obs.getTotalDmg() == 0
    assert obs.lastdamage is None

    obs.update(5)
    assert obs.getTotalDmg() == 5
    assert obs.lastdamage == 5

    obs.update(3)
    assert obs.getTotalDmg() == 8
    assert obs.lastdamage == 3
