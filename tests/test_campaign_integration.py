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

        

if __name__ == "__main__":
    class MockMonkeyPatch:
        def chdir(self, path): os.chdir(path)
    test_campaign_integration(MockMonkeyPatch())
