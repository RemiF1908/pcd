"""Tests pour le système de campagne simplifié."""

import pytest
import tempfile
import os
from src.model.campaign_manager import Campaign
from src.model.level import LevelBuilder


def test_campaign_init():
    """Test l'initialisation de Campaign."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        f.write('{"campaign": {"name": "Test"}, "levels": []}')
        filepath = f.name

    try:
        campaign = Campaign(filepath)
        assert campaign.campaign_json_path == filepath
        assert campaign._current_level_num == 0
        assert campaign._completed_levels == []
    finally:
        os.unlink(filepath)


def test_campaign_init_nonexistent_file():
    """Test l'initialisation avec un fichier inexistant."""
    campaign = Campaign("nonexistent.json")
    assert campaign._data is None
    assert campaign._completed_levels == []


def test_get_campaign_info():
    """Test la récupération des infos de campagne."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        f.write('''{
            "campaign": {
                "name": "Test Campaign",
                "description": "Test Description"
            },
            "levels": []
        }''')
        filepath = f.name

    try:
        campaign = Campaign(filepath)
        info = campaign.get_campaign_info()
        assert info["name"] == "Test Campaign"
        assert info["description"] == "Test Description"
    finally:
        os.unlink(filepath)


def test_complete_level():
    """Test la complétion d'un niveau."""
    campaign = Campaign("nonexistent.json")
    
    assert campaign.is_completed(1) is False
    campaign.complete_level(1)
    assert campaign.is_completed(1) is True
    assert 1 in campaign.get_completed_levels()


def test_complete_level_no_duplicate():
    """Test qu'on ne peut pas compléter un niveau deux fois."""
    campaign = Campaign("nonexistent.json")
    
    campaign.complete_level(1)
    campaign.complete_level(1)
    
    assert len(campaign._completed_levels) == 1
    assert len(campaign.get_completed_levels()) == 1


def test_get_completed_levels():
    """Test la récupération des niveaux complétés."""
    campaign = Campaign("nonexistent.json")
    
    campaign.complete_level(1)
    campaign.complete_level(2)
    campaign.complete_level(3)
    
    completed = campaign.get_completed_levels()
    assert completed == [1, 2, 3]
    assert len(completed) == 3


def test_reset():
    """Test la réinitialisation de la campagne."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        f.write('{"campaign": {"name": "Test"}, "levels": [{"id": 1}]}')
        filepath = f.name

    try:
        campaign = Campaign(filepath)
        campaign._current_level_num = 5
        campaign.complete_level(1)
        campaign.complete_level(2)
        
        campaign.reset()
        
        assert campaign._current_level_num == 0
        assert campaign._completed_levels == []
        assert campaign.is_completed(1) is False
    finally:
        os.unlink(filepath)


def test_load_level_nonexistent():
    """Test le chargement d'un niveau inexistant."""
    campaign = Campaign("nonexistent.json")
    level = campaign.load_level(999)
    assert level is None


def test_load_level_no_dungeon_file():
    """Test le chargement d'un niveau sans fichier de donjon."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        f.write('''{
            "campaign": {"name": "Test"},
            "levels": [{"id": 1, "name": "Level 1", "budget": 100, "difficulty": 1}]
        }''')
        filepath = f.name

    try:
        campaign = Campaign(filepath)
        level = campaign.load_level(1)
        assert level is None
    finally:
        os.unlink(filepath)


def test_load_level_dungeon_file_not_exists():
    """Test le chargement d'un niveau avec un fichier de donjon inexistant."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        f.write('''{
            "campaign": {"name": "Test"},
            "levels": [{"id": 1, "dungeon_file": "nonexistent", "budget": 100, "difficulty": 1, "heroes": []}]
        }''')
        filepath = f.name

    try:
        campaign = Campaign(filepath)
        level = campaign.load_level(1)
        assert level is None
    finally:
        os.unlink(filepath)


def test_load_level_success():
    """Test le chargement réussi d'un niveau."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        f.write('''{
            "campaign": {"name": "Test"},
            "levels": [{
                "id": 1,
                "dungeon_file": "level1_dungeon",
                "budget": 200,
                "difficulty": 2,
                "heroes": [{"pv": 50, "strategy": "random"}]
            }]
        }''')
        campaign_file = f.name

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json", dir="./save") as f:
        f.write('''{
            "dimension": [5, 5],
            "entry": [0, 0],
            "exit": [4, 4],
            "grid": []
        }''')
        dungeon_file = f.name.split("/")[-1].replace(".json", "")

    try:
        campaign = Campaign(campaign_file)
        level = campaign.load_level(1)
        
        assert level is not None
        assert level.budget_tot == 200
        assert level.difficulty == 2
        assert level.nb_heroes == 1
        assert campaign._current_level_num == 1
    finally:
        os.unlink(campaign_file)
        os.unlink(f"./save/{dungeon_file}.json")


def test_load_next_level():
    """Test le chargement du niveau suivant."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        f.write('''{
            "campaign": {"name": "Test"},
            "levels": [
                {
                    "id": 1,
                    "dungeon_file": "level1_dungeon",
                    "budget": 100,
                    "difficulty": 1,
                    "heroes": [{"pv": 50, "strategy": "random"}]
                },
                {
                    "id": 2,
                    "dungeon_file": "level2_dungeon",
                    "budget": 200,
                    "difficulty": 2,
                    "heroes": [{"pv": 80, "strategy": "shortest"}]
                }
            ]
        }''')
        campaign_file = f.name

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json", dir="./save") as f:
        f.write('''{
            "dimension": [5, 5],
            "entry": [0, 0],
            "exit": [4, 4],
            "grid": []
        }''')
        dungeon_file = f.name.split("/")[-1].replace(".json", "")

    try:
        campaign = Campaign(campaign_file)
        
        level1 = campaign.load_level(1)
        assert level1 is not None
        assert level1.budget_tot == 100
        assert campaign._current_level_num == 1
        
        level2 = campaign.load_next_level()
        assert level2 is not None
        assert level2.budget_tot == 200
        assert campaign._current_level_num == 2
    finally:
        os.unlink(campaign_file)
        os.unlink(f"./save/{dungeon_file}.json")


def test_is_completed():
    """Test la vérification de complétion d'un niveau."""
    campaign = Campaign("nonexistent.json")
    
    assert campaign.is_completed(5) is False
    
    campaign.complete_level(5)
    assert campaign.is_completed(5) is True
