"""
Test d'intégration complet du système de campagne avec LevelController.
"""

import os
import tempfile
import json
from src.model.campaign_manager import CampaignManager
from src.model.dungeon import Dungeon
from src.model.level import Level, LevelBuilder
from src.simulation import Simulation
from src.controller.game_controller import GameController
from src.controller.level_controller import LevelController
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


def test_campaign_integration():
    """Test l'intégration complète de la campagne avec LevelController."""

    import shutil

    original_cwd = os.getcwd()
    save_dir = "./save"

    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
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

        # Test LevelController
        level_controller = LevelController(campaign_path)
        assert level_controller.campaign_manager is not None

        campaign_info = level_controller.get_campaign_info()
        assert campaign_info["name"] == "Test Campaign"

        level1_info = level_controller.get_current_level()
        assert level1_info is not None
        assert level1_info["id"] == 1
        assert level_controller.get_level_budget() == 200

        # Test GameController avec LevelController
        simulation = Simulation(level=Level())
        game_controller = GameController(MagicMock(), simulation)

        # Charger le niveau via LevelController + GameController
        dungeon_file = level_controller.get_level_dungeon_file()
        assert dungeon_file is not None
        assert dungeon_file == "level1"

        imported_dungeon = game_controller.import_dungeon(dungeon_file)
        assert imported_dungeon is not None
        assert imported_dungeon.dimension == (5, 5)

        # Créer le niveau avec LevelBuilder
        builder = LevelBuilder()
        builder.set_dungeon(imported_dungeon)
        builder.set_budget(level_controller.get_level_budget())
        builder.set_difficulty(level_controller.get_level_difficulty())

        for hero_config in level_controller.get_level_heroes_config():
            pv = hero_config.get("pv", 100)
            strategy = hero_config.get("strategy", "random")
            builder.add_hero(pv=pv, strategy=strategy, coord=imported_dungeon.entry)

        level = builder.build()
        game_controller.setup_level(level)

        assert simulation.dungeon.dimension == (5, 5)
        assert len(simulation.heroes) == 1
        assert simulation.heroes[0].pv_total == 50

        # Test victoire
        wave_result = {
            "heroesKilled": 1,
            "heroesSurvived": 0,
            "construction_cost": 50,
            "score": 5000,
            "turns": 10
        }

        assert level_controller.check_win_condition(wave_result) is True
        assert 1 in level_controller.get_completed_levels()

        # Test niveau suivant
        next_level = level_controller.advance_to_next_level()
        assert next_level is not None
        assert next_level["id"] == 2

        assert level_controller.has_more_levels() is False

        # Configurer niveau 2
        dungeon_file = level_controller.get_level_dungeon_file()
        imported_dungeon = game_controller.import_dungeon(dungeon_file)

        builder = LevelBuilder()
        builder.set_dungeon(imported_dungeon)
        builder.set_budget(level_controller.get_level_budget())
        builder.set_difficulty(level_controller.get_level_difficulty())

        for hero_config in level_controller.get_level_heroes_config():
            pv = hero_config.get("pv", 100)
            strategy = hero_config.get("strategy", "random")
            builder.add_hero(pv=pv, strategy=strategy, coord=imported_dungeon.entry)

        level = builder.build()
        game_controller.setup_level(level)

        assert simulation.dungeon.dimension == (6, 6)
        assert len(simulation.heroes) == 1
        assert simulation.heroes[0].pv_total == 80

        print("✅ Test d'intégration de campagne avec LevelController réussi")


if __name__ == "__main__":
    test_campaign_integration()
