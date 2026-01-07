"""Tests pour le pattern Command."""

import pytest
import tempfile
import os
import json
from unittest.mock import patch, MagicMock, mock_open
from src.model.level import Level, LevelPresets
from src.commands.Command import Command
from src.commands.placeEntity import placeEntity
from src.commands.removeEntity import removeEntity
from src.commands.startWave import startWave
from src.commands.stopWave import stopWave
from src.commands.resetDungeon import resetDungeon
from src.commands.exportDungeon import exportDungeon
from src.commands.importDungeon import importDungeon
from src.commands.getDungeonList import getDungeonList
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

    command = placeEntity(dungeon, wall, position)
    command.execute()

    cell = dungeon.get_cell(position)
    assert cell.entity is wall
    assert not dungeon.is_Walkable(position)


def test_place_entity_trap():
    """Test la commande placeEntity avec un piège."""
    dungeon = create_test_dungeon()
    trap = EntityFactory.create_trap(damage=20)
    position = (1, 1)

    command = placeEntity(dungeon, trap, position)
    command.execute()

    cell = dungeon.get_cell(position)
    assert cell.entity is trap
    assert cell.get_damage() == 20


def test_place_entity_floor():
    """Test la commande placeEntity avec un sol (remplace un mur)."""
    dungeon = create_test_dungeon()
    dungeon.place_entity(EntityFactory.create_wall(), (2, 2))

    floor = EntityFactory.create_floor()
    command = placeEntity(dungeon, floor, (2, 2))
    command.execute()

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

    command = startWave(mock_simulation)
    command.execute()

    mock_simulation.launch.assert_called_once()


def test_stop_wave_command():
    """Test la commande stopWave."""
    mock_simulation = MagicMock()

    command = stopWave(mock_simulation)
    command.execute()

    mock_simulation.stop.assert_called_once()


def test_stop_wave_command_with_exception():
    """Test stopWave avec simulation invalide."""
    mock_simulation = MagicMock()
    mock_simulation.running = True
    mock_simulation.stop = MagicMock(side_effect=AttributeError())

    command = stopWave(mock_simulation)
    try:
        command.execute()
    except Exception:
        pass


def test_reset_dungeon_command():
    """Test la commande resetDungeon."""
    dungeon = create_test_dungeon()
    dungeon.place_entity(EntityFactory.create_wall(), (0, 1))
    dungeon.place_entity(EntityFactory.create_trap(damage=15), (1, 1))

    command = resetDungeon(dungeon)
    command.execute()

    assert dungeon.is_Walkable((0, 1))
    assert not dungeon.get_cell((1, 1)).is_dangerous()


def test_export_dungeon_command():
    """Test la commande exportDungeon."""
    dungeon = create_test_dungeon() 

    filename = "test_dungeon_export"
    
    expected_filepath = f"./save/{filename}.json"

    try:
        command = exportDungeon(dungeon, filename)
        command.execute()

        assert os.path.exists(expected_filepath), f"Le fichier {expected_filepath} n'a pas été créé"

        with open(expected_filepath, "r") as f:
            content = json.load(f)

        assert content is not None
        assert "dimension" in content
        assert content["dimension"] == list(dungeon.dimension) # Convert tuple to list for JSON comparison

    finally:
        # Nettoyage
        if os.path.exists(expected_filepath):
            os.unlink(expected_filepath)


def test_import_dungeon_command():
    """Test la commande importDungeon."""
    from src.controller.game_controller import GameController
    from src.simulation import Simulation

    dungeon = create_test_dungeon()
    level = LevelPresets().easy(dungeon)
    simulation = Simulation(level, dungeon=dungeon)
    interface = MagicMock()

    controller = GameController(interface, simulation)

    controller.place_trap((2, 2), damage=20)
    controller.place_wall((3, 3))

    filename = "test_dungeon_export"
    
    expected_filepath = f"./save/{filename}.json"

    try:
        controller.export_dungeon(filename)
        imported_dungeon = controller.import_dungeon(filename)

        assert imported_dungeon is not None
        assert imported_dungeon.dimension == dungeon.dimension
        assert imported_dungeon.entry == dungeon.entry
        assert imported_dungeon.exit == dungeon.exit

        cell = imported_dungeon.get_cell((2, 2))
        assert isinstance(cell.entity, Trap)
        assert cell.entity.damage == 20

        cell = imported_dungeon.get_cell((3, 3))
        assert isinstance(cell.entity, Wall)
    finally:
        if os.path.exists(expected_filepath):
            os.unlink(expected_filepath)

def test_getDungeonList_command():
    """Test la commande getDungeonList."""

    with tempfile.TemporaryDirectory() as tempdir:
        filenames = ["dungeon1.json", "dungeon2.json"] 
        
        for fname in filenames:
            with open(os.path.join(tempdir, fname), "w") as f:
                f.write("{}")

        command = getDungeonList()
        command.save_directory = tempdir
        command.execute()

        expected_dungeons = ["dungeon1", "dungeon2"]
        assert sorted(command.result) == sorted(expected_dungeons)

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

    place_command = placeEntity(dungeon, wall, (2, 2))
    place_command.execute()

    assert not dungeon.is_Walkable((2, 2))

    remove_command = removeEntity(dungeon, (2, 2))
    remove_command.execute()

    assert dungeon.is_Walkable((2, 2))


def test_multiple_commands_with_invoker():
    """Test workflow complet avec GameInvoker."""
    dungeon = create_test_dungeon()
    invoker = GameInvoker()

    invoker.push_command(placeEntity(dungeon, EntityFactory.create_wall(), (1, 1)))

    invoker.push_command(
        placeEntity(dungeon, EntityFactory.create_trap(damage=10), (2, 2))
    )

    invoker.push_command(resetDungeon(dungeon))
    invoker.execute()

    assert dungeon.is_Walkable((1, 1))
    assert not dungeon.get_cell((2, 2)).is_dangerous()
