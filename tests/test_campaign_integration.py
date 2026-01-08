"""
Test d'intégration complet du système de campagne avec Campaign.
"""

import os
import tempfile
import json
from src.model.campaign_manager import Campaign
from src.simulation import Simulation
from src.model.level import Level
from src.controller.game_controller import GameController
from unittest.mock import MagicMock


def create_test_dungeon_file(rows=5, cols=5, filepath="test_dungeon.json"):
    """Crée un fichier de donjon de test."""
    grid = []
    for r in range(rows):
        row = []
        for c in range(cols):
            row.append({"type": "Floor", "position": [r, c]})
        grid.append(row)

    dungeon_data = {
        "dimension": [rows, cols],
        "entry": [0, 0],
        "exit": [rows - 1, cols - 1],
        "grid": grid
    }

    with open(filepath, "w") as f:
        json.dump(dungeon_data, f)


def test_campaign_integration(monkeypatch):
    """Test l'intégration complète de la campagne avec Campaign."""

    save_dir = "./save"

    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.chdir(tmpdir)
        
        os.makedirs(save_dir, exist_ok=True)

        dungeon1_path = os.path.join(save_dir, "level1.json")
        dungeon2_path = os.path.join(save_dir, "level2.json")
        campaign_path = "campaign.json"

        create_test_dungeon_file(5, 5, dungeon1_path)
        create_test_dungeon_file(6, 6, dungeon2_path)

        campaign_data = {
            "campaign": {
                "name": "Test Campaign",
                "description": "Test integration"
            },
            "levels": [
                {
                    "id": 1,
                    "name": "Level 1",
                    "difficulty": 1,
                    "budget": 200,
                    "dungeon_file": "level1",
                    "heroes": [{"pv": 50, "strategy": "random"}]
                },
                {
                    "id": 2,
                    "name": "Level 2",
                    "difficulty": 2,
                    "budget": 150,
                    "dungeon_file": "level2",
                    "heroes": [{"pv": 80, "strategy": "safest"}]
                }
            ]
        }

        with open(campaign_path, "w") as f:
            json.dump(campaign_data, f)

        campaign = Campaign(campaign_path)

        campaign_info = campaign.get_campaign_info()
        assert campaign_info["name"] == "Test Campaign"

        level1 = campaign.load_level(1)
        assert level1 is not None
        assert level1.difficulty == 1
        assert level1.budget_tot == 200
        assert level1.dungeon is not None

        simulation = Simulation(level=level1, dungeon=level1.dungeon)
        game_controller = GameController(MagicMock(), simulation)

        assert simulation.dungeon.dimension == (5, 5)
        assert len(simulation.heroes) == 1
        assert simulation.heroes[0].pv_total == 50

        wave_result = {
            "heroesKilled": 1,
            "heroesSurvived": 0,
            "construction_cost": 50,
            "score": 5000,
            "turns": 10
        }

        campaign.complete_level(1)
        assert campaign.is_completed(1) is True

        level2 = campaign.load_next_level()
        assert level2 is not None
        assert level2.difficulty == 2
        assert level2.budget_tot == 150
        assert level2.dungeon is not None

        simulation2 = Simulation(level=level2, dungeon=level2.dungeon)
        game_controller2 = GameController(MagicMock(), simulation2)

        assert simulation2.dungeon.dimension == (6, 6)
        assert len(simulation2.heroes) == 1
        assert simulation2.heroes[0].pv_total == 80

        campaign.complete_level(2)
        assert campaign.is_completed(2) is True

        completed = campaign.get_completed_levels()
        assert 1 in completed
        assert 2 in completed



if __name__ == "__main__":
    class MockMonkeyPatch:
        def chdir(self, path): os.chdir(path)
    test_campaign_integration(MockMonkeyPatch())
