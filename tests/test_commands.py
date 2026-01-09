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
    mock_simulation = MagicMock()
    mock_simulation.isSimStarted = False
    mock_simulation.current_budget = 100
    command = placeEntity(dungeon, wall, position, mock_simulation)
    command.execute(MagicMock())

    cell = dungeon.get_cell(position)
    assert cell.entity is wall
    assert not dungeon.is_Walkable(position)


def test_place_entity_trap():
    """Test la commande placeEntity avec un piège."""
    dungeon = create_test_dungeon()
    trap = EntityFactory.create_trap(damage=20)
    position = (1, 1)
    mock_simulation = MagicMock()
    mock_simulation.current_budget = 100
    mock_simulation.isSimStarted = False

    command = placeEntity(dungeon, trap, position, mock_simulation)
    command.execute(MagicMock())

    cell = dungeon.get_cell(position)
    assert cell.entity is trap
    assert cell.get_damage() == 20


def test_place_entity_floor():
    """Test la commande placeEntity avec un sol (remplace un mur)."""
    dungeon = create_test_dungeon()
    dungeon.place_entity(EntityFactory.create_wall(), (2, 2))

    floor = EntityFactory.create_floor()
    mock_simulation = MagicMock()
    mock_simulation.isSimStarted = False
    mock_simulation.current_budget = 100
    command = placeEntity(dungeon, floor, (2, 2), mock_simulation)
    command.execute(MagicMock())

    assert dungeon.is_Walkable((2, 2))


def test_remove_entity_command():
    """Test la commande removeEntity."""
    dungeon = create_test_dungeon()
    dungeon.place_entity(EntityFactory.create_wall(), (1, 1))
    mock_simulation = MagicMock()
    mock_simulation.isSimStarted = False
    mock_simulation.current_budget = 100
    command = removeEntity(dungeon, (1, 1), mock_simulation)
    command.execute(MagicMock())

    assert dungeon.is_Walkable((1, 1))


def test_remove_entity_from_floor():
    """Test removeEntity quand on supprime un sol (doit rester un sol)."""
    dungeon = create_test_dungeon()
    mock_simulation = MagicMock()
    mock_simulation.isSimStarted = False
    
    command = removeEntity(dungeon, (1, 1), mock_simulation)
    command.execute(MagicMock())

    cell = dungeon.get_cell((1, 1))
    assert isinstance(cell.entity, Floor)


def test_start_wave_command():
    """Test la commande startWave."""
    mock_simulation = MagicMock()
    mock_simulation.isSimStarted = False
    mock_simulation.step.return_value = None

    command = startWave(mock_simulation)
    command.execute(MagicMock())

    mock_simulation.step.assert_called_once()


def test_stop_wave_command():
    """Test la commande stopWave."""
    mock_simulation = MagicMock()

    command = stopWave(mock_simulation)
    command.execute(MagicMock())

    mock_simulation.stop.assert_called_once()


def test_stop_wave_command_with_exception():
    """Test stopWave avec simulation invalide."""
    mock_simulation = MagicMock()
    mock_simulation.running = True
    mock_simulation.stop = MagicMock(side_effect=AttributeError())

    command = stopWave(mock_simulation)
    try:
        command.execute(MagicMock())
    except Exception:
        pass


def test_reset_dungeon_command():
    """Test la commande resetDungeon."""
    dungeon = create_test_dungeon()
    dungeon.place_entity(EntityFactory.create_wall(), (0, 1))
    dungeon.place_entity(EntityFactory.create_trap(damage=15), (1, 1))

    command = resetDungeon(dungeon)
    command.execute(MagicMock())

    assert dungeon.is_Walkable((0, 1))
    assert not dungeon.get_cell((1, 1)).is_dangerous()


def test_export_dungeon_command():
    """Test la commande exportDungeon."""
    dungeon = create_test_dungeon()

    filename = "test_dungeon_export"

    expected_filepath = f"./save/{filename}.json"

    try:
        campaign_progress = [1, 2, 3]
        command = exportDungeon(dungeon, filename, campaign_progress)
        mock_controller = MagicMock()
        command.execute(mock_controller)

        assert os.path.exists(expected_filepath), (
            f"Le fichier {expected_filepath} n'a pas été créé"
        )

        with open(expected_filepath, "r") as f:
            content = json.load(f)

        assert content is not None
        assert "dimension" in content
        assert content["dimension"] == list(
            dungeon.dimension
        )  # Convert tuple to list for JSON comparison
        assert "campaign_progress" in content
        assert content["campaign_progress"] == campaign_progress

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
        campaign_progress = [1, 2, 3]
        command = exportDungeon(dungeon, filename, campaign_progress)
        mock_controller = MagicMock()
        command.execute(mock_controller)
        
        import_command = importDungeon(filename)
        import_command.execute(mock_controller)
        imported_dungeon = import_command.result

        assert imported_dungeon is not None
        assert imported_dungeon.dimension == dungeon.dimension
        assert imported_dungeon.entry == dungeon.entry
        assert imported_dungeon.exit == dungeon.exit

        cell = imported_dungeon.get_cell((2, 2))
        assert isinstance(cell.entity, Trap)
        assert cell.entity.damage == 20

        cell = imported_dungeon.get_cell((3, 3))
        assert isinstance(cell.entity, Wall)
        
        # Vérifier la progression de campagne
        assert import_command.campaign_progress == campaign_progress
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
        command.execute(MagicMock())

        expected_dungeons = ["dungeon1", "dungeon2"]
        assert sorted(command.result) == sorted(expected_dungeons)


def test_game_invoker_initialization():
    """Test l'initialisation de GameInvoker."""
    mock_controller = MagicMock()
    invoker = GameInvoker(mock_controller)

    assert invoker.game_controller is mock_controller
    assert invoker.history == []
    assert invoker.commandstack == []


def test_game_invoker_push_command():
    """Test push_command de GameInvoker."""
    mock_controller = MagicMock()
    invoker = GameInvoker(mock_controller)
    command = MagicMock()

    invoker.push_command(command)

    assert len(invoker.commandstack) == 1
    assert invoker.commandstack[0] is command


def test_game_invoker_push_multiple_commands():
    """Test push_command avec plusieurs commandes."""
    mock_controller = MagicMock()
    invoker = GameInvoker(mock_controller)
    command1 = MagicMock()
    command2 = MagicMock()
    command3 = MagicMock()

    invoker.push_command(command1)
    invoker.push_command(command2)
    invoker.push_command(command3)

    assert len(invoker.commandstack) == 3


def test_game_invoker_execute_single():
    """Test execute avec une seule commande."""
    mock_controller = MagicMock()
    invoker = GameInvoker(mock_controller)
    command = MagicMock()

    invoker.push_command(command)
    invoker.execute()

    command.execute.assert_called_once_with(mock_controller)
    assert len(invoker.history) == 1
    assert invoker.history[0] is command
    assert len(invoker.commandstack) == 0


def test_game_invoker_execute_multiple():
    """Test execute avec plusieurs commandes."""
    mock_controller = MagicMock()
    invoker = GameInvoker(mock_controller)
    command1 = MagicMock()
    command2 = MagicMock()
    command3 = MagicMock()

    invoker.push_command(command1)
    invoker.push_command(command2)
    invoker.push_command(command3)
    invoker.execute()

    command1.execute.assert_called_once_with(mock_controller)
    command2.execute.assert_called_once_with(mock_controller)
    command3.execute.assert_called_once_with(mock_controller)

    assert len(invoker.history) == 3
    assert len(invoker.commandstack) == 0


def test_game_invoker_execute_clears_stack():
    """Test que execute vide la stack après exécution."""
    mock_controller = MagicMock()
    invoker = GameInvoker(mock_controller)
    command = MagicMock()

    invoker.push_command(command)
    assert len(invoker.commandstack) == 1

    invoker.execute()
    assert len(invoker.commandstack) == 0


def test_game_invoker_history_preserved():
    """Test que l'historique est préservé entre les executes."""
    mock_controller = MagicMock()
    invoker = GameInvoker(mock_controller)
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
    mock_simulation = MagicMock()
    mock_simulation.current_budget = 100
    mock_simulation.isSimStarted = False
    mock_controller = MagicMock()

    place_command = placeEntity(dungeon, wall, (2, 2), mock_simulation)
    place_command.execute(mock_controller)

    assert not dungeon.is_Walkable((2, 2))

    remove_command = removeEntity(dungeon, (2, 2), mock_simulation)
    remove_command.execute(mock_controller)

    assert dungeon.is_Walkable((2, 2))


def test_multiple_commands_with_invoker():
    """Test workflow complet avec GameInvoker."""
    dungeon = create_test_dungeon()
    mock_simulation = MagicMock()
    mock_simulation.current_budget = 100
    mock_simulation.isSimStarted = False
    mock_controller = MagicMock()
    invoker = GameInvoker(mock_controller)

    invoker.push_command(
        placeEntity(dungeon, EntityFactory.create_wall(), (1, 1), mock_simulation)
    )

    invoker.push_command(
        placeEntity(
            dungeon, EntityFactory.create_trap(damage=10), (2, 2), mock_simulation
        )
    )

    invoker.push_command(resetDungeon(dungeon))
    invoker.execute()

    assert dungeon.is_Walkable((1, 1))
    assert not dungeon.get_cell((2, 2)).is_dangerous()


def test_import_dungeon_elementary():
    """Test la commande importDungeon avec un donjon élémentaire."""
    # Créer la commande d'import avec le fichier de test (sans extension)
    command = importDungeon("dungeontest")
    mock_controller = MagicMock()
    
    # Exécuter la commande
    command.execute(mock_controller)
    
    # Récupérer le donjon importé
    imported_dungeon = command.result
    
    # Vérifier que le donjon a bien été importé
    assert imported_dungeon is not None
    assert imported_dungeon.dimension == (3, 3)
    assert imported_dungeon.entry == (0, 0)
    assert imported_dungeon.exit == (2, 2)
    
    # Vérifier les cellules
    cell_floor = imported_dungeon.get_cell((0, 0))
    assert isinstance(cell_floor.entity, Floor)
    
    cell_trap = imported_dungeon.get_cell((1, 1))
    assert isinstance(cell_trap.entity, Trap)
    assert cell_trap.entity.damage == 5
    
    cell_wall = imported_dungeon.get_cell((2, 1))
    assert isinstance(cell_wall.entity, Wall)
