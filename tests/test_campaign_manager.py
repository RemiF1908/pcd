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


def test_is_completed():
    """Test la vérification de complétion d'un niveau."""
    campaign = Campaign("nonexistent.json")
    
    assert campaign.is_completed(5) is False
    
    campaign.complete_level(5)
    assert campaign.is_completed(5) is True
