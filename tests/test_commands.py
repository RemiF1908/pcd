"""Tests pour le pattern Command."""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock, mock_open
from src.commands.Command import Command
from src.commands.placeEntity import placeEntity
from src.commands.removeEntity import removeEntity
from src.commands.startWave import startWave
from src.commands.stopWave import stopWave
from src.commands.resetDungeon import resetDungeon
from src.commands.exportDungeon import exportDungeon
from src.commands.importDungeon import importDungeon
from src.commands.GameInvoker import GameInvoker
from src.model.dungeon import Dungeon
from src.model.cell import Cell
from src.model.floor import Floor
from src.model.wall import Wall
from src.model.trap import Trap
from src.model.entity_factory import EntityFactory


def create_test_dungeon(rows=5, cols=5):
    """Helper pour créer un donjon de test."""
    grid = [[Cell((r, c), None) for c in range(cols)] for r in range(rows)]
    return Dungeon(
        dimension=(rows, cols), grid=grid, entry=(0, 0), exit=(rows - 1, cols - 1)
    )


def test_command_is_abstract():
    """Test que Command est bien une classe abstraite."""
    with pytest.raises(TypeError):
        Command()


def test_place_entity_command():
    """Test la commande placeEntity."""
    dungeon = create_test_dungeon()
    wall = EntityFactory.create_wall()
    position = (2, 3)

    command = placeEntity()
    command.execute(dungeon, wall, position)

    cell = dungeon.get_cell(position)
    assert cell.entity is wall
    assert not dungeon.is_Walkable(position)


def test_place_entity_trap():
    """Test la commande placeEntity avec un piège."""
    dungeon = create_test_dungeon()
    trap = EntityFactory.create_trap(damage=20)
    position = (1, 1)

    command = placeEntity()
    command.execute(dungeon, trap, position)

    cell = dungeon.get_cell(position)
    assert cell.entity is trap
    assert cell.get_damage() == 20


def test_place_entity_floor():
    """Test la commande placeEntity avec un sol (remplace un mur)."""
    dungeon = create_test_dungeon()
    dungeon.place_entity(EntityFactory.create_wall(), (2, 2))

    floor = EntityFactory.create_floor()
    command = placeEntity()
    command.execute(dungeon, floor, (2, 2))

    assert dungeon.is_Walkable((2, 2))


def test_remove_entity_command():
    """Test la commande removeEntity."""
    dungeon = create_test_dungeon()
    dungeon.place_entity(EntityFactory.create_wall(), (1, 1))

    command = removeEntity(dungeon, (1, 1))
    command.execute()

    assert dungeon.is_Walkable((1, 1))


def test_remove_entity_from_floor():
    """Test removeEntity quand on supprime un sol (doit rester un sol)."""
    dungeon = create_test_dungeon()

    command = removeEntity(dungeon, (1, 1))
    command.execute()

    cell = dungeon.get_cell((1, 1))
    assert isinstance(cell.entity, Floor)


def test_start_wave_command():
    """Test la commande startWave."""
    mock_simulation = MagicMock()
    mock_simulation.launch.return_value = None

    command = startWave()
    command.execute(mock_simulation)

    mock_simulation.launch.assert_called_once()


def test_stop_wave_command():
    """Test la commande stopWave."""
    mock_simulation = MagicMock()
    mock_simulation.running = True

    command = stopWave()
    command.execute(mock_simulation)

    assert mock_simulation.running is False


def test_stop_wave_command_with_exception():
    """Test stopWave avec simulation invalide."""
    mock_simulation = MagicMock()
    mock_simulation.running = True
    mock_simulation.running = MagicMock(side_effect=AttributeError())

    command = stopWave()
    try:
        command.execute(mock_simulation)
    except Exception:
        pass


def test_reset_dungeon_command():
    """Test la commande resetDungeon."""
    dungeon = create_test_dungeon()
    dungeon.place_entity(EntityFactory.create_wall(), (0, 1))
    dungeon.place_entity(EntityFactory.create_trap(damage=15), (1, 1))

    command = resetDungeon()
    command.execute(dungeon)

    assert dungeon.is_Walkable((0, 1))
    assert not dungeon.get_cell((1, 1)).is_dangerous()


def test_export_dungeon_command():
    """Test la commande exportDungeon."""
    dungeon = MagicMock()
    dungeon.serialize.return_value = '{"test": "data"}'

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        filepath = f.name

    try:
        command = exportDungeon()
        command.filepath = filepath
        command.execute(dungeon, filepath)

        with open(filepath, "r") as f:
            content = f.read()

        assert content == '{"test": "data"}'
    finally:
        if os.path.exists(filepath):
            os.unlink(filepath)


def test_import_dungeon_command():
    """Test la commande importDungeon."""
    test_data = '{"test": "import"}'

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        f.write(test_data)
        filepath = f.name

    try:
        command = importDungeon()
        result = command.execute(filepath)

        assert result == test_data
    finally:
        if os.path.exists(filepath):
            os.unlink(filepath)


def test_game_invoker_initialization():
    """Test l'initialisation de GameInvoker."""
    invoker = GameInvoker()

    assert invoker.history == []
    assert invoker.commandstack == []


def test_game_invoker_push_command():
    """Test push_command de GameInvoker."""
    invoker = GameInvoker()
    command = MagicMock()

    invoker.push_command(command)

    assert len(invoker.commandstack) == 1
    assert invoker.commandstack[0] is command


def test_game_invoker_push_multiple_commands():
    """Test push_command avec plusieurs commandes."""
    invoker = GameInvoker()
    command1 = MagicMock()
    command2 = MagicMock()
    command3 = MagicMock()

    invoker.push_command(command1)
    invoker.push_command(command2)
    invoker.push_command(command3)

    assert len(invoker.commandstack) == 3


def test_game_invoker_execute_single():
    """Test execute avec une seule commande."""
    invoker = GameInvoker()
    command = MagicMock()

    invoker.push_command(command)
    invoker.execute()

    command.execute.assert_called_once()
    assert len(invoker.history) == 1
    assert invoker.history[0] is command
    assert len(invoker.commandstack) == 0


def test_game_invoker_execute_multiple():
    """Test execute avec plusieurs commandes."""
    invoker = GameInvoker()
    command1 = MagicMock()
    command2 = MagicMock()
    command3 = MagicMock()

    invoker.push_command(command1)
    invoker.push_command(command2)
    invoker.push_command(command3)
    invoker.execute()

    command1.execute.assert_called_once()
    command2.execute.assert_called_once()
    command3.execute.assert_called_once()

    assert len(invoker.history) == 3
    assert len(invoker.commandstack) == 0


def test_game_invoker_execute_clears_stack():
    """Test que execute vide la stack après exécution."""
    invoker = GameInvoker()
    command = MagicMock()

    invoker.push_command(command)
    assert len(invoker.commandstack) == 1

    invoker.execute()
    assert len(invoker.commandstack) == 0


def test_game_invoker_history_preserved():
    """Test que l'historique est préservé entre les executes."""
    invoker = GameInvoker()
    command1 = MagicMock()
    command2 = MagicMock()

    invoker.push_command(command1)
    invoker.execute()

    invoker.push_command(command2)
    invoker.execute()

    assert len(invoker.history) == 2
    assert invoker.history[0] is command1
    assert invoker.history[1] is command2


def test_place_entity_then_remove():
    """Test workflow complet: place puis remove."""
    dungeon = create_test_dungeon()
    wall = EntityFactory.create_wall()

    place_command = placeEntity()
    place_command.execute(dungeon, wall, (2, 2))

    assert not dungeon.is_Walkable((2, 2))

    remove_command = removeEntity(dungeon, (2, 2))
    remove_command.execute()

    assert dungeon.is_Walkable((2, 2))


def test_multiple_commands_with_invoker():
    """Test workflow complet avec GameInvoker."""
    dungeon = create_test_dungeon()
    invoker = GameInvoker()

    invoker.push_command(placeEntity())
    invoker.commandstack[-1].execute(dungeon, EntityFactory.create_wall(), (1, 1))

    invoker.push_command(placeEntity())
    invoker.commandstack[-1].execute(
        dungeon, EntityFactory.create_trap(damage=10), (2, 2)
    )

    invoker.push_command(resetDungeon())
    invoker.commandstack[-1].execute(dungeon)

    assert dungeon.is_Walkable((1, 1))
    assert not dungeon.get_cell((2, 2)).is_dangerous()
