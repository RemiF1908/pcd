"""
Module d'affichage de donjon en TUI avec la librairie curses.

Usage:
    from src.view.tui.dungeon_display import display_dungeon
    from src.model.dungeon import Dungeon

    # Créer un donjon...
    dungeon = Dungeon(...)

    # Afficher avec curses (bloquant, appuyer sur une touche pour quitter)
    display_dungeon(dungeon)

    # Ou utiliser directement dans une boucle curses existante :
    # draw_dungeon(stdscr, dungeon, start_y=0, start_x=0)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable

import curses

if TYPE_CHECKING:
    from src.model.dungeon import Dungeon


class ColorPair(Enum):
    """Paires de couleurs pour curses."""

    FLOOR = 1
    WALL = 2
    TRAP = 3
    MONSTER = 4
    ENTRANCE = 5
    EXIT = 6
    HERO = 7

    @classmethod
    def init_curses_colors(cls) -> None:
        """Initialise les paires de couleurs curses."""
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(cls.FLOOR.value, curses.COLOR_WHITE, -1)
        curses.init_pair(cls.WALL.value, curses.COLOR_WHITE, -1)
        curses.init_pair(cls.TRAP.value, curses.COLOR_RED, -1)
        curses.init_pair(cls.MONSTER.value, curses.COLOR_MAGENTA, -1)
        curses.init_pair(cls.ENTRANCE.value, curses.COLOR_GREEN, -1)
        curses.init_pair(cls.EXIT.value, curses.COLOR_CYAN, -1)
        curses.init_pair(cls.HERO.value, curses.COLOR_YELLOW, -1)


@dataclass
class LegendEntry:
    """Entrée de légende."""

    symbol: str
    label: str
    color_pair: ColorPair


class Legend:
    """Légende des symboles du donjon."""

    ENTRIES = [
        LegendEntry(". ", "Floor", ColorPair.FLOOR),
        LegendEntry("# ", "Wall", ColorPair.WALL),
        LegendEntry("^ ", "Trap", ColorPair.TRAP),
        LegendEntry("M ", "Monster", ColorPair.MONSTER),
        LegendEntry("E ", "Entrance", ColorPair.ENTRANCE),
        LegendEntry("S ", "Exit", ColorPair.EXIT),
        LegendEntry("@ ", "Hero", ColorPair.HERO),
    ]

    @classmethod
    def get_symbol_for(cls, entity_type: str) -> str:
        """Retourne le symbole pour un type d'entité."""
        for entry in cls.ENTRIES:
            if entry.label.upper() == entity_type:
                return entry.symbol
        return "+"


def _get_cell_display(
    dungeon: "Dungeon", pos: tuple[int, int], hero_set: set[tuple[int, int]]
) -> tuple[str, int]:
    """Détermine le symbole et la couleur pour une cellule."""
    if pos in hero_set:
        return Legend.get_symbol_for("HERO"), ColorPair.HERO.value
    if pos == dungeon.entry:
        return Legend.get_symbol_for("ENTRANCE"), ColorPair.ENTRANCE.value
    if pos == dungeon.exit:
        return Legend.get_symbol_for("EXIT"), ColorPair.EXIT.value

    cell = dungeon.get_cell(pos)
    if cell.entity is not None:
        return cell.entity.get_display_char(), cell.entity.get_color_id()

    return "+", 0


def _draw_char(stdscr, y: int, x: int, char: str, color_pair: int = 0) -> None:
    """Dessine un caractère avec une couleur."""
    try:
        stdscr.addch(y, x, char, curses.color_pair(color_pair))
    except curses.error:
        pass


def _draw_str(stdscr, y: int, x: int, text: str, attr: int = 0) -> None:
    """Dessine une chaîne de caractères."""
    try:
        stdscr.addstr(y, x, text, attr)
    except curses.error:
        pass


def _draw_reverse_char(stdscr, y: int, x: int, length: int = 1) -> None:
    """Inverse la couleur d'un caractère."""
    try:
        stdscr.chgat(y, x, length, curses.A_REVERSE)
    except curses.error:
        pass


def _init_colors() -> None:
    """Initialise les paires de couleurs curses."""
    curses.start_color()
    curses.use_default_colors()

    # Paire 1 : Floor (gris sur fond par défaut)
    curses.init_pair(1, curses.COLOR_WHITE, -1)
    # Paire 2 : Wall (blanc brillant)
    curses.init_pair(2, curses.COLOR_WHITE, -1)
    # Paire 3 : Trap (rouge)
    curses.init_pair(3, curses.COLOR_RED, -1)
    # Paire 4 : Monster (magenta)
    curses.init_pair(4, curses.COLOR_MAGENTA, -1)
    # Paire 5 : Entrance (vert)
    curses.init_pair(5, curses.COLOR_GREEN, -1)
    # Paire 6 : Exit (cyan)
    curses.init_pair(6, curses.COLOR_CYAN, -1)
    # Paire 7 : Héros (jaune)
    curses.init_pair(7, curses.COLOR_YELLOW, -1)


def draw_dungeon(
    stdscr,
    dungeon: "Dungeon",
    start_y: int = 1,
    start_x: int = 1,
    hero_positions: list[tuple[int, int]] | None = None,
) -> None:
    """Dessine le donjon sur la fenêtre curses.

    Args:
        stdscr: Fenêtre curses standard.
        dungeon: Instance de Dungeon à afficher.
        start_y: Ligne de départ pour l'affichage.
        start_x: Colonne de départ pour l'affichage.
        hero_positions: Liste optionnelle de positions (row, col) des héros.
    """
    rows, cols = dungeon.dimension
    hero_set = set(hero_positions) if hero_positions else set()

    for row in range(rows):
        for col in range(cols):
            pos = (row, col)
            symbol, color_pair = _get_cell_display(dungeon, pos, hero_set)
            _draw_char(stdscr, start_y + row, start_x + col * 2, symbol, color_pair)


def draw_legend(stdscr, start_y: int, start_x: int) -> None:
    """Affiche la légende des symboles."""
    _draw_str(stdscr, start_y, start_x, "=== Légende ===", curses.A_BOLD)

    for i, entry in enumerate(Legend.ENTRIES):
        _draw_str(
            stdscr,
            start_y + 1 + i,
            start_x,
            entry.symbol,
            curses.color_pair(entry.color_pair.value),
        )
        _draw_str(stdscr, start_y + 1 + i, start_x + 2, entry.label)


class Layout:
    """Constantes de layout pour l'affichage."""

    TITLE_Y = 0
    TITLE_X = 1
    DUNGEON_START_Y = 2
    DUNGEON_START_X = 1
    LEGEND_X_OFFSET = 3
    STATUS_START_Y = 12
    DEFAULT_FOOTER_Y = 20


def draw_status(stdscr, start_y: int, start_x: int, info: dict[str, Any]) -> None:
    """Affiche des informations de status (tour, héros restants, etc.).

    Args:
        stdscr: Fenêtre curses.
        start_y, start_x: Position.
        info: Dictionnaire avec les infos à afficher.
              Ex: {"turn": 5, "heroes_alive": 2, "budget": 100}
    """
    _draw_str(stdscr, start_y, start_x, "=== Status ===", curses.A_BOLD)

    for line, (key, value) in enumerate(info.items(), 1):
        _draw_str(stdscr, start_y + line, start_x, f"{key}: {value}")


def display_dungeon(
    dungeon: "Dungeon",
    hero_positions: list[tuple[int, int]] | None = None,
    status_info: dict[str, Any] | None = None,
) -> None:
    """Affiche le donjon dans le terminal (bloquant).

    Initialise curses, dessine le donjon, la légende et le status,
    puis attend une touche pour quitter.

    Args:
        dungeon: Le donjon à afficher.
        hero_positions: Positions des héros (optionnel).
        status_info: Infos de status (optionnel).
    """

    def _main(stdscr):
        curses.curs_set(0)
        ColorPair.init_curses_colors()
        stdscr.clear()

        rows, cols = dungeon.dimension

        _draw_str(
            stdscr, Layout.TITLE_Y, Layout.TITLE_X, "🏰 DUNGEON MANAGER", curses.A_BOLD
        )

        draw_dungeon(
            stdscr,
            dungeon,
            Layout.DUNGEON_START_Y,
            Layout.DUNGEON_START_X,
            hero_positions,
        )

        legend_x = Layout.DUNGEON_START_Y + cols * 2 + Layout.LEGEND_X_OFFSET
        draw_legend(stdscr, Layout.DUNGEON_START_Y, legend_x)

        if status_info:
            draw_status(stdscr, Layout.STATUS_START_Y, legend_x, status_info)

        footer_y = max(rows + Layout.DUNGEON_START_Y + 2, Layout.DEFAULT_FOOTER_Y)
        _draw_str(
            stdscr,
            footer_y,
            Layout.DUNGEON_START_X,
            "Appuyez sur une touche pour quitter...",
            curses.A_DIM,
        )

        stdscr.refresh()
        stdscr.getch()

    curses.wrapper(_main)


class TUIView:
    """Interface TUI interactive avec gestion des inputs utilisateur."""

    def __init__(self, game_controller: Any):
        """Initialise la vue TUI.

        Args:
            game_controller: Contrôleur de jeu pour exécuter les commandes (obligatoire).
        """
        if game_controller is None:
            raise ValueError("game_controller est obligatoire")

        self.game_controller = game_controller
        self.dungeon = game_controller.dungeon
        self.running = False
        self.hero_positions: list[tuple[int, int]] = []
        self.status_info: dict[str, Any] = {}
        self.cursor_pos: tuple[int, int] = (0, 0)

        # Mapping des touches vers les commandes
        self.key_bindings: dict[int, Callable[[], None]] = {
            ord("q"): self._quit,
            ord("s"): self._start_wave,
            ord("x"): self._stop_wave,
            ord("r"): self._reset_dungeon,
            ord("e"): self._export_dungeon,
            ord("i"): self._import_dungeon,
            curses.KEY_UP: self._move_cursor_up,
            curses.KEY_DOWN: self._move_cursor_down,
            curses.KEY_LEFT: self._move_cursor_left,
            curses.KEY_RIGHT: self._move_cursor_right,
            ord("t"): self._place_trap,
            ord("w"): self._place_wall,
            ord("d"): self._remove_entity,
        }

    def _quit(self) -> None:
        self.running = False

    def _start_wave(self) -> None:
        self.game_controller.start_wave()

    def _stop_wave(self) -> None:
        self.game_controller.stop()

    def _reset_dungeon(self) -> None:
        self.game_controller.reset_dungeon()

    def _export_dungeon(self) -> None:
        self.game_controller.export_dungeon()

    def _import_dungeon(self) -> None:
        self.game_controller.import_dungeon()

    def _move_cursor(self, delta_row: int, delta_col: int) -> None:
        """Déplace le curseur selon les deltas fournis."""
        row, col = self.cursor_pos
        max_row, max_col = self.dungeon.dimension[0] - 1, self.dungeon.dimension[1] - 1
        new_row = max(0, min(max_row, row + delta_row))
        new_col = max(0, min(max_col, col + delta_col))
        self.cursor_pos = (new_row, new_col)

    def _move_cursor_up(self) -> None:
        self._move_cursor(-1, 0)

    def _move_cursor_down(self) -> None:
        self._move_cursor(1, 0)

    def _move_cursor_left(self) -> None:
        self._move_cursor(0, -1)

    def _move_cursor_right(self) -> None:
        self._move_cursor(0, 1)

    def _place_trap(self) -> None:
        self.game_controller.place_trap(self.cursor_pos, damage=10)

    def _place_wall(self) -> None:
        self.game_controller.place_wall(self.cursor_pos)

    def _remove_entity(self) -> None:
        self.game_controller.remove_entity(self.cursor_pos)

    def _draw_cursor(self, stdscr, start_y: int, start_x: int) -> None:
        row, col = self.cursor_pos
        _draw_reverse_char(stdscr, start_y + row, start_x + col * 2)

    def _draw_help(self, stdscr, start_y: int, start_x: int) -> None:
        help_text = [
            ("=== Commandes ===", curses.A_BOLD),
            ("q: Quitter", 0),
            ("s: Start Wave", 0),
            ("x: Stop Wave", 0),
            ("r: Reset", 0),
            ("e: Export", 0),
            ("i: Import", 0),
            ("", 0),
            ("=== Déplacement curseur ===", curses.A_BOLD),
            ("Flèches: Déplacer", 0),
            ("", 0),
            ("=== Placer entités ===", curses.A_BOLD),
            ("t: Trap (piège)", 0),
            ("w: Wall (mur)", 0),
            ("d: Delete (supprimer)", 0),
        ]

        for i, (text, attr) in enumerate(help_text):
            _draw_str(stdscr, start_y + i, start_x, text, attr)

    def update_hero_positions(self, positions: list[tuple[int, int]]) -> None:
        self.hero_positions = positions

    def update_status_info(self, info: dict[str, Any]) -> None:
        self.status_info = info

    def render(self, stdscr) -> None:
        stdscr.clear()

        rows, cols = self.dungeon.dimension

        _draw_str(
            stdscr, Layout.TITLE_Y, Layout.TITLE_X, "🏰 DUNGEON MANAGER", curses.A_BOLD
        )

        draw_dungeon(
            stdscr,
            self.dungeon,
            Layout.DUNGEON_START_Y,
            Layout.DUNGEON_START_X,
            hero_positions=self.hero_positions,
        )

        self._draw_cursor(stdscr, Layout.DUNGEON_START_Y, Layout.DUNGEON_START_X)

        legend_x = Layout.DUNGEON_START_Y + cols * 2 + Layout.LEGEND_X_OFFSET
        draw_legend(stdscr, Layout.DUNGEON_START_Y, legend_x)

        if self.status_info:
            draw_status(stdscr, Layout.STATUS_START_Y, legend_x, self.status_info)

        help_y = max(rows + Layout.DUNGEON_START_Y + 2, Layout.DEFAULT_FOOTER_Y)
        self._draw_help(stdscr, help_y, Layout.DUNGEON_START_X)

        _draw_str(
            stdscr,
            help_y - 1,
            Layout.DUNGEON_START_X,
            f"Curseur: {self.cursor_pos}",
            curses.A_DIM,
        )

        stdscr.refresh()
