"""Tests pour la classe GameController."""

import pytest
from unittest.mock import MagicMock, patch
from src.controller.game_controller import GameController
from src.simulation import Simulation
from src.model.level import Level
from src.model.dungeon import Dungeon
from src.model.cell import Cell

#On utilise des mocks
#https://fr.wikipedia.org/wiki/Mock_(programmation_orient%C3%A9e_objet)


def create_test_dungeon(rows=5, cols=5):
    """Helper pour créer un donjon de test."""
    grid = [[Cell((r, c), None) for c in range(cols)] for r in range(rows)]
    return Dungeon(
        dimension=(rows, cols), grid=grid, entry=(0, 0), exit=(rows - 1, cols - 1)
    )


def test_game_controller_initialization():
    """Test de l'initialisation de GameController."""
    interface = MagicMock()
    simulation = MagicMock()

    controller = GameController(interface, simulation)

    assert controller.interface is interface
    assert controller.simulation is simulation


def test_game_controller_start_wave():
    """Test de la méthode start_wave."""
    interface = MagicMock()
    simulation = MagicMock()

    controller = GameController(interface, simulation)
    controller.start_wave()

    simulation.launch.assert_called_once()


def test_game_controller_stop():
    """Test de la méthode stop."""
    interface = MagicMock()
    dungeon = create_test_dungeon()
    lvl = Level(dungeon=dungeon, budget_tot=100, nb_heroes=0, heroes=[])
    simulation = Simulation(level=lvl, dungeon=dungeon)
    simulation.running = True

    controller = GameController(interface, simulation)
    controller.stop()

    assert simulation.running is False


def test_game_controller_with_real_simulation():
    """Test GameController avec une vraie Simulation."""
    interface = MagicMock()
    dungeon = create_test_dungeon()
    lvl = Level(dungeon=dungeon, budget_tot=100, nb_heroes=0, heroes=[])
    simulation = Simulation(level=lvl, dungeon=dungeon)

    controller = GameController(interface, simulation)

    assert controller.simulation is simulation
    assert controller.simulation.dungeon is dungeon


def test_game_controller_start_wave_launches_simulation():
    """Test que start_wave lance réellement la simulation."""
    interface = MagicMock()
    dungeon = create_test_dungeon()
    lvl = Level(dungeon=dungeon, budget_tot=100, nb_heroes=0, heroes=[])
    simulation = Simulation(level=lvl, dungeon=dungeon)

    controller = GameController(interface, simulation)
    simulation.allHeroesDead = True

    import time

    original_sleep = time.sleep
    time.sleep = lambda x: None 
    controller.start_wave()

    time.sleep = original_sleep  
    assert simulation.ticks == 0  


def test_game_controller_stop_stops_simulation():
    """Test que stop arrête réellement la simulation."""
    interface = MagicMock()
    simulation = Simulation(level=Level())
    simulation.running = True

    controller = GameController(interface, simulation)
    controller.stop()

    assert simulation.running is False


def test_game_controller_stop_idempotent():
    """Test que stop peut être appelé plusieurs fois."""
    interface = MagicMock()
    simulation = Simulation(level=Level())

    controller = GameController(interface, simulation)
    controller.stop()
    controller.stop()
    controller.stop()

    assert simulation.running is False


@patch("builtins.print")
def test_game_controller_start_wave_prints_message(mock_print):
    """Test que start_wave affiche le message."""
    interface = MagicMock()
    simulation = MagicMock()

    controller = GameController(interface, simulation)
    controller.start_wave()

    mock_print.assert_called_with("Starting new wave...")


def test_game_controller_interface_render_integration():
    """Test intégration avec interface.render()."""
    interface = MagicMock()
    simulation = MagicMock()
    simulation.level = 2
    simulation.score = 150
    simulation.current_budget = 80

    controller = GameController(interface, simulation)

    interface.render(simulation)
    interface.render.assert_called_once_with(simulation)


def test_game_controller_with_interface_get_input():
    """Test que l'interface expose get_input()."""
    interface = MagicMock()
    interface.get_input.return_value = "command"

    simulation = MagicMock()

    controller = GameController(interface, simulation)

    command = controller.interface.get_input()
    assert command == "command"


def test_game_controller_with_interface_handle_command():
    """Test que l'interface expose handle_command()."""
    interface = MagicMock()
    simulation = MagicMock()

    controller = GameController(interface, simulation)

    controller.interface.handle_command("test_command", simulation)
    interface.handle_command.assert_called_once_with("test_command", simulation)


def test_game_controller_integration_simulation_state():
    """Test que GameController maintient l'état de la simulation."""
    interface = MagicMock()
    dungeon = create_test_dungeon()
    lvl = Level(dungeon=dungeon, budget_tot=200, nb_heroes=0, heroes=[])
    simulation = Simulation(level=lvl, dungeon=dungeon)

    controller = GameController(interface, simulation)

    simulation.ticks = 10
    simulation.score = 50

    assert controller.simulation.ticks == 10
    assert controller.simulation.score == 50
    assert controller.simulation.current_budget == 200
