"""Configuration pytest pour les tests du projet Dungeon Manager."""

import pytest


def pytest_configure(config):
    """Enregistre les markers personnalisés."""
    config.addinivalue_line(
        "markers", "curses: tests nécessitant un terminal curses (requiert -s)"
    )


def pytest_collection_modifyitems(config, items):
    """Skip automatiquement les tests curses si capture est activée."""
    if config.getoption("capture") != "no":
        skip_curses = pytest.mark.skip(
            reason="Tests curses requièrent: pytest -s (ou --capture=no)"
        )
        for item in items:
            if "curses" in item.keywords:
                item.add_marker(skip_curses)
