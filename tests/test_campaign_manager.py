"""Tests pour le système de campagne."""

import pytest
import tempfile
import os
from src.model.campaign_manager import CampaignManager


def test_campaign_manager_init():
    """Test l'initialisation du CampaignManager."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        f.write('{"campaign": {"name": "Test"}, "levels": []}')
        filepath = f.name

    try:
        manager = CampaignManager(filepath)
        assert manager.campaign_json_path == filepath
        assert manager.current_level_index == 0
        assert manager.completed_levels == []
    finally:
        os.unlink(filepath)


def test_campaign_load_success():
    """Test le chargement réussi d'une campagne."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        f.write('''{
            "campaign": {"name": "Test Campaign"},
            "levels": [{"id": 1, "name": "Level 1"}]
        }''')
        filepath = f.name

    try:
        manager = CampaignManager(filepath)
        success = manager.load_campaign()
        assert success is True
        assert manager.campaign_data is not None
        assert len(manager.get_levels()) == 1
    finally:
        os.unlink(filepath)


def test_campaign_load_failure():
    """Test le chargement d'un fichier inexistant."""
    manager = CampaignManager("nonexistent.json")
    success = manager.load_campaign()
    assert success is False
    assert manager.campaign_data is None


def test_get_current_level():
    """Test la récupération du niveau actuel."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        f.write('''{
            "campaign": {"name": "Test"},
            "levels": [
                {"id": 1, "name": "Level 1"},
                {"id": 2, "name": "Level 2"}
            ]
        }''')
        filepath = f.name

    try:
        manager = CampaignManager(filepath)
        manager.load_campaign()

        level = manager.get_current_level()
        assert level is not None
        assert level["id"] == 1

        manager.current_level_index = 1
        level = manager.get_current_level()
        assert level["id"] == 2

        manager.current_level_index = 2
        level = manager.get_current_level()
        assert level is None
    finally:
        os.unlink(filepath)


def test_get_level_by_id():
    """Test la récupération d'un niveau par ID."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        f.write('''{
            "campaign": {"name": "Test"},
            "levels": [
                {"id": 1, "name": "Level 1"},
                {"id": 2, "name": "Level 2"}
            ]
        }''')
        filepath = f.name

    try:
        manager = CampaignManager(filepath)
        manager.load_campaign()

        level = manager.get_level_by_id(1)
        assert level is not None
        assert level["name"] == "Level 1"

        level = manager.get_level_by_id(99)
        assert level is None
    finally:
        os.unlink(filepath)


def test_complete_level():
    """Test la complétion d'un niveau."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        f.write('{"campaign": {"name": "Test"}, "levels": [{"id": 1}]}')
        filepath = f.name

    try:
        manager = CampaignManager(filepath)
        manager.load_campaign()

        assert 1 not in manager.completed_levels
        manager.complete_level(1)
        assert 1 in manager.completed_levels
        manager.complete_level(1)
        assert len(manager.completed_levels) == 1
    finally:
        os.unlink(filepath)


def test_advance_to_next_level():
    """Test l'avancement au niveau suivant."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        f.write('''{
            "campaign": {"name": "Test"},
            "levels": [
                {"id": 1, "name": "Level 1"},
                {"id": 2, "name": "Level 2"}
            ]
        }''')
        filepath = f.name

    try:
        manager = CampaignManager(filepath)
        manager.load_campaign()

        assert manager.current_level_index == 0
        next_level = manager.advance_to_next_level()
        assert next_level is not None
        assert next_level["id"] == 2
        assert manager.current_level_index == 1

        next_level = manager.advance_to_next_level()
        assert next_level is None
    finally:
        os.unlink(filepath)


def test_check_win_condition():
    """Test la vérification de condition de victoire."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        f.write('''{
            "campaign": {"name": "Test"},
            "levels": [{"id": 1, "name": "Level 1"}]
        }''')
        filepath = f.name

    try:
        manager = CampaignManager(filepath)
        manager.load_campaign()
        level_config = manager.get_current_level()

        wave_result_win = {"heroesSurvived": 0}
        assert manager.check_win_condition(wave_result_win, level_config) is True

        wave_result_lose = {"heroesSurvived": 2}
        assert manager.check_win_condition(wave_result_lose, level_config) is False
    finally:
        os.unlink(filepath)


def test_has_more_levels():
    """Test la vérification de niveaux restants."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        f.write('''{
            "campaign": {"name": "Test"},
            "levels": [{"id": 1}, {"id": 2}]
        }''')
        filepath = f.name

    try:
        manager = CampaignManager(filepath)
        manager.load_campaign()

        assert manager.has_more_levels() is True

        manager.current_level_index = 1
        assert manager.has_more_levels() is False
    finally:
        os.unlink(filepath)


def test_reset_progress():
    """Test la réinitialisation de progression."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        f.write('{"campaign": {"name": "Test"}, "levels": [{"id": 1}]}')
        filepath = f.name

    try:
        manager = CampaignManager(filepath)
        manager.load_campaign()
        manager.complete_level(1)
        manager.current_level_index = 5

        manager.reset_progress()
        assert manager.current_level_index == 0
        assert manager.completed_levels == []
    finally:
        os.unlink(filepath)


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
        manager = CampaignManager(filepath)
        manager.load_campaign()

        info = manager.get_campaign_info()
        assert info["name"] == "Test Campaign"
        assert info["description"] == "Test Description"
    finally:
        os.unlink(filepath)
