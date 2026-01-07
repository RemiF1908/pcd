"""Tests pour l'affichage TUI du donjon avec curses.

IMPORTANT: Ces tests nécessitent un vrai terminal.
Lancer avec: pytest tests/test_dungeon_display.py -s
"""

import sys
import curses
import pytest
from src.model.dungeon import Dungeon
from src.model.cell import Cell
from src.model.floor import Floor
from src.model.wall import Wall
from src.model.trap import Trap
from src.model.entity_factory import EntityFactory
from src.view.tui.dungeon_display import (
    draw_dungeon,
    draw_legend,
    _init_colors,
    TUIView,
)


# Skip si pas de terminal (pytest capture les I/O)
_skip_no_terminal = pytest.mark.skipif(
    not sys.stdout.isatty(),
    reason="Tests curses requièrent: pytest -s (ou --capture=no)",
)


def create_test_dungeon():
    """Cree un donjon de test."""
    rows, cols = 8, 12

    # Créer la grille vide (sera remplie de Floor par le constructeur de Dungeon)
    grid = [[Cell((r, c), None) for c in range(cols)] for r in range(rows)]

    # Créer le donjon (cela va remplir toutes les cellules avec Floor())
    dungeon = Dungeon(
        dimension=(rows, cols), grid=grid, entry=(0, 0), exit=(rows - 1, cols - 1)
    )

    # Maintenant ajouter les murs
    for c in range(3, 8):
        dungeon.place_entity(EntityFactory.create_wall(), (3, c))
    for r in range(3, 6):
        dungeon.place_entity(EntityFactory.create_wall(), (r, 7))

    dungeon.place_entity(EntityFactory.create_wall(), (1, 5))
    dungeon.place_entity(EntityFactory.create_wall(), (5, 2))

    # Ajouter les pièges
    dungeon.place_entity(EntityFactory.create_trap(damage=10), (2, 4))
    dungeon.place_entity(EntityFactory.create_trap(damage=15), (5, 3))
    dungeon.place_entity(EntityFactory.create_trap(damage=20), (6, 9))

    hero_positions = [(1, 1), (2, 3), (4, 5)]
    return dungeon, hero_positions


@_skip_no_terminal
def test_curses_draw_dungeon():
    """Test affichage curses du donjon."""
    dungeon, hero_positions = create_test_dungeon()

    def _test(stdscr):
        curses.curs_set(0)
        _init_colors()
        stdscr.clear()
        draw_dungeon(
            stdscr, dungeon, start_y=1, start_x=1, hero_positions=hero_positions
        )
        assert chr(stdscr.inch(1, 1) & 0xFF) == "E"
        rows, cols = dungeon.dimension
        assert chr(stdscr.inch(1 + rows - 1, 1 + (cols - 1) * 2) & 0xFF) == "S"
        assert chr(stdscr.inch(1 + 1, 1 + 1 * 2) & 0xFF) == "@"
        assert chr(stdscr.inch(1 + 3, 1 + 5 * 2) & 0xFF) == "#"
        assert chr(stdscr.inch(1 + 2, 1 + 4 * 2) & 0xFF) == "^"

    curses.wrapper(_test)


@_skip_no_terminal
def test_curses_colors():
    """Test initialisation couleurs curses."""

    def _test(stdscr):
        _init_colors()
        assert curses.has_colors()
        for pair_id in range(1, 8):
            fg, bg = curses.pair_content(pair_id)
            assert isinstance(fg, int)

    curses.wrapper(_test)


@_skip_no_terminal
def test_curses_legend():
    """Test affichage legende curses."""

    def _test(stdscr):
        _init_colors()
        stdscr.clear()
        draw_legend(stdscr, start_y=0, start_x=0)
        content = ""
        for row in range(8):
            for col in range(20):
                try:
                    content += chr(stdscr.inch(row, col) & 0xFF)
                except Exception:
                    pass
        assert "." in content and "#" in content and "^" in content

    curses.wrapper(_test)


@_skip_no_terminal
def test_curses_polymorphism():
    """Test polymorphisme entites avec curses."""

    def _test(stdscr):
        _init_colors()
        stdscr.clear()
        floor = EntityFactory.create_floor()
        wall = EntityFactory.create_wall()
        trap = EntityFactory.create_trap(damage=10)

        stdscr.addch(
            0, 0, floor.get_display_char(), curses.color_pair(floor.get_color_id())
        )
        stdscr.addch(
            0, 2, wall.get_display_char(), curses.color_pair(wall.get_color_id())
        )
        stdscr.addch(
            0, 4, trap.get_display_char(), curses.color_pair(trap.get_color_id())
        )

        assert chr(stdscr.inch(0, 0) & 0xFF) == "."
        assert chr(stdscr.inch(0, 2) & 0xFF) == "#"
        assert chr(stdscr.inch(0, 4) & 0xFF) == "^"

    curses.wrapper(_test)


@_skip_no_terminal
def test_curses_display_full_dungeon():
    """Test affichage complet du donjon avec curses - entree, sortie, heros, murs, pieges."""
    dungeon, hero_positions = create_test_dungeon()

    def _test(stdscr):
        curses.curs_set(0)
        _init_colors()
        stdscr.clear()

        # Titre
        stdscr.addstr(0, 1, "TEST DUNGEON DISPLAY", curses.A_BOLD)

        # Dessiner le donjon avec curses
        draw_dungeon(
            stdscr, dungeon, start_y=2, start_x=1, hero_positions=hero_positions
        )

        # Dessiner la legende
        rows, cols = dungeon.dimension
        legend_x = 2 + cols * 2 + 3
        draw_legend(stdscr, start_y=2, start_x=legend_x)

        # Info (utiliser try/except pour éviter erreurs si terminal trop petit)
        try:
            stdscr.addstr(
                rows + 4,
                1,
                "E=Entree S=Sortie @=Hero #=Mur ^=Piege .=Sol",
                curses.A_DIM,
            )
            stdscr.addstr(
                rows + 5, 1, "Appuyez sur une touche pour continuer...", curses.A_DIM
            )
        except curses.error:
            pass

        stdscr.refresh()
        stdscr.getch()  # Attend une touche

        # Verifications
        # Entree en (0,0)
        assert chr(stdscr.inch(2, 1) & 0xFF) == "E"
        # Sortie en (7,11)
        assert chr(stdscr.inch(2 + 7, 1 + 11 * 2) & 0xFF) == "S"
        # Hero en (1,1)
        assert chr(stdscr.inch(2 + 1, 1 + 1 * 2) & 0xFF) == "@"
        # Mur en (3,5)
        assert chr(stdscr.inch(2 + 3, 1 + 5 * 2) & 0xFF) == "#"
        # Piege en (2,4)
        assert chr(stdscr.inch(2 + 2, 1 + 4 * 2) & 0xFF) == "^"
        # Sol en (0,1)
        assert chr(stdscr.inch(2 + 0, 1 + 1 * 2) & 0xFF) == "."

    curses.wrapper(_test)


def demo_display():
    """Demo affichage curses."""
    from src.view.tui.dungeon_display import display_dungeon

    dungeon, hero_positions = create_test_dungeon()
    status_info = {"Tour": 1, "Heros": 3, "Budget": 150}
    print("Demo curses - Appuyez sur Entree...")
    input()
    display_dungeon(dungeon, hero_positions=hero_positions, status_info=status_info)
    print("Termine!")


if __name__ == "__main__":
    demo_display()


def test_tui_view_creation():
    """Test creation d'une instance TUIView."""
    dungeon, _ = create_test_dungeon()
    from src.controller.game_controller import GameController
    from src.simulation import Simulation

    simulation = Simulation(dungeon=dungeon, budget_tot=100, nb_heroes=0, heroes=[])
    gc = GameController(interface=None, simulation=simulation)
    tui = TUIView(game_controller=gc)

    assert tui.dungeon == dungeon
    assert tui.game_controller == gc
    assert tui.running == False
    assert tui.cursor_pos == (0, 0)


def test_tui_view_requires_controller():
    """Test que TUIView necessite un controller."""
    dungeon, _ = create_test_dungeon()
    try:
        tui = TUIView(game_controller=None)
        assert False, "Devrait lever ValueError"
    except ValueError:
        pass


def test_tui_view_cursor_movement():
    """Test mouvement du curseur TUIView."""
    dungeon, _ = create_test_dungeon()
    from src.controller.game_controller import GameController
    from src.simulation import Simulation

    simulation = Simulation(dungeon=dungeon, budget_tot=100, nb_heroes=0, heroes=[])
    gc = GameController(interface=None, simulation=simulation)
    tui = TUIView(game_controller=gc)

    # Test initial position
    assert tui.cursor_pos == (0, 0)

    # Test mouvements
    tui._move_cursor_down()
    assert tui.cursor_pos == (1, 0)

    tui._move_cursor_right()
    assert tui.cursor_pos == (1, 1)

    tui._move_cursor_up()
    assert tui.cursor_pos == (0, 1)

    tui._move_cursor_left()
    assert tui.cursor_pos == (0, 0)

    # Test limites
    tui._move_cursor_up()
    assert tui.cursor_pos == (0, 0)

    tui._move_cursor_left()
    assert tui.cursor_pos == (0, 0)


def test_tui_view_key_bindings():
    """Test que les bindings de touches sont definis."""
    dungeon, _ = create_test_dungeon()
    from src.controller.game_controller import GameController
    from src.simulation import Simulation

    simulation = Simulation(dungeon=dungeon, budget_tot=100, nb_heroes=0, heroes=[])
    gc = GameController(interface=None, simulation=simulation)
    tui = TUIView(game_controller=gc)

    # Verifier que les touches importantes sont definies
    assert ord("q") in tui.key_bindings
    assert ord("s") in tui.key_bindings
    assert ord("x") in tui.key_bindings
    assert ord("r") in tui.key_bindings
    assert ord("e") in tui.key_bindings
    assert ord("i") in tui.key_bindings
    assert ord("t") in tui.key_bindings
    assert ord("w") in tui.key_bindings
    assert ord("d") in tui.key_bindings
    assert curses.KEY_UP in tui.key_bindings
    assert curses.KEY_DOWN in tui.key_bindings
    assert curses.KEY_LEFT in tui.key_bindings
    assert curses.KEY_RIGHT in tui.key_bindings


def test_tui_view_update_methods():
    """Test les methodes de mise a jour de TUIView."""
    dungeon, _ = create_test_dungeon()
    from src.controller.game_controller import GameController
    from src.simulation import Simulation

    simulation = Simulation(dungeon=dungeon, budget_tot=100, nb_heroes=0, heroes=[])
    gc = GameController(interface=None, simulation=simulation)
    tui = TUIView(game_controller=gc)

    # Test update_hero_positions
    positions = [(1, 2), (3, 4), (5, 6)]
    tui.update_hero_positions(positions)
    assert tui.hero_positions == positions

    # Test update_status_info
    status = {"Tour": 5, "Héros": 2, "Budget": 150}
    tui.update_status_info(status)
    assert tui.status_info == status


def test_tui_view_place_entity():
    """Test placement d'entites via TUIView."""
    dungeon, _ = create_test_dungeon()
    from src.controller.game_controller import GameController
    from src.simulation import Simulation

    simulation = Simulation(dungeon=dungeon, budget_tot=100, nb_heroes=0, heroes=[])
    gc = GameController(interface=None, simulation=simulation)
    tui = TUIView(game_controller=gc)

    # Deplacer le curseur
    tui.cursor_pos = (2, 3)

    # Placer un mur
    tui._place_wall()
    cell = dungeon.get_cell((2, 3))
    from src.model.wall import Wall

    assert isinstance(cell.entity, Wall)

    # Placer un piege
    tui.cursor_pos = (4, 5)
    tui._place_trap()
    cell = dungeon.get_cell((4, 5))
    from src.model.trap import Trap

    assert isinstance(cell.entity, Trap)


def test_tui_view_remove_entity():
    """Test suppression d'entites via TUIView."""
    dungeon, _ = create_test_dungeon()
    from src.controller.game_controller import GameController
    from src.simulation import Simulation

    simulation = Simulation(dungeon=dungeon, budget_tot=100, nb_heroes=0, heroes=[])
    gc = GameController(interface=None, simulation=simulation)
    tui = TUIView(game_controller=gc)

    # Placer un mur
    from src.model.entity_factory import EntityFactory

    dungeon.place_entity(EntityFactory.create_wall(), (3, 3))

    # Supprimer le mur
    tui.cursor_pos = (3, 3)
    tui._remove_entity()

    # Verifier que c'est maintenant un sol
    from src.model.floor import Floor

    cell = dungeon.get_cell((3, 3))
    assert isinstance(cell.entity, Floor)


def test_tui_view_controller_integration():
    """Test l'integration TUIView avec GameController."""
    dungeon, _ = create_test_dungeon()
    from src.controller.game_controller import GameController
    from src.simulation import Simulation

    simulation = Simulation(dungeon=dungeon, budget_tot=100, nb_heroes=0, heroes=[])
    gc = GameController(interface=None, simulation=simulation)
    tui = TUIView(game_controller=gc)

    # Verifier que le controller a acces au donjon
    assert gc.dungeon == dungeon

    # Test que les methodes du controller sont accessibles depuis la vue
    tui.cursor_pos = (2, 2)

    # Placer un mur via la vue (qui appelle le controller)
    tui._place_wall()
    cell = dungeon.get_cell((2, 2))
    from src.model.wall import Wall

    assert isinstance(cell.entity, Wall)

    # Supprimer via la vue
    tui._remove_entity()
    cell = dungeon.get_cell((2, 2))
    from src.model.floor import Floor

    assert isinstance(cell.entity, Floor)
