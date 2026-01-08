"""
Module d'affichage de donjon en TUI avec la librairie curses.


    # Afficher avec curses (bloquant, appuyer sur une touche pour quitter)
"""

from __future__ import annotations
from src.simulation import Simulation
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable
import curses


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
        LegendEntry(".", "Floor", ColorPair.FLOOR),
        LegendEntry("#", "Wall", ColorPair.WALL),
        LegendEntry("^", "Trap", ColorPair.TRAP),
        LegendEntry("M", "Monster", ColorPair.MONSTER),
        LegendEntry("E", "Entrance", ColorPair.ENTRANCE),
        LegendEntry("S", "Exit", ColorPair.EXIT),
        LegendEntry("@", "Hero", ColorPair.HERO),
    ]

    @classmethod
    def get_symbol_for(cls, entity_type: str) -> str:
        """Retourne le symbole pour un type d'entité."""
        for entry in cls.ENTRIES:
            if entry.label.upper() == entity_type:
                return entry.symbol
        return "+"


def _get_cell_display(grid : list[list[tuple[str,int]]], heros_pos : list[tuple[int, int]], entry_pos: tuple[int, int], exit_pos: tuple[int, int], pos: tuple[int, int]) -> tuple[str, int]:
    """Détermine le symbole et la couleur pour une cellule."""
    if pos in heros_pos:
        return Legend.get_symbol_for("HERO"), ColorPair.HERO.value
    if pos == entry_pos:
        return Legend.get_symbol_for("ENTRANCE"), ColorPair.ENTRANCE.value
    if pos == exit_pos:
        return Legend.get_symbol_for("EXIT"), ColorPair.EXIT.value
    cell = grid[pos[0]][pos[1]]
    if cell is not None:
        return cell

    return ("+", 0)


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


def draw_simulation(
    stdscr,
    hero_positions: list[tuple[int, int]],
    dimension: tuple[int, int],
    grid : list[list[tuple[str,int]]],
    entry_pos: tuple[int, int],
    exit_pos: tuple[int, int],
    start_y: int = 1,
    start_x: int = 1
) -> None:
    """Dessine le donjon sur la fenêtre curses.

    Args:
        stdscr: Fenêtre curses standard.
        simulation: Instance de Simulation à afficher.
        start_y: Ligne de départ pour l'affichage.
        start_x: Colonne de départ pour l'affichage.
    """

    rows, cols = dimension
    hero_set = set(hero_positions) if hero_positions else set()

    for row in range(rows):
        for col in range(cols):
            pos = (row, col)
            symbol, color_pair = grid[row][col]
            if pos in hero_set:
                symbol, color_pair = Legend.get_symbol_for("HERO"), ColorPair.HERO.value
            elif pos == entry_pos:
                symbol, color_pair = Legend.get_symbol_for("ENTRANCE"), ColorPair.ENTRANCE.value
            elif pos == exit_pos:
                symbol, color_pair = Legend.get_symbol_for("EXIT"), ColorPair.EXIT.value
            _draw_str(
                stdscr,
                start_y + row,
                start_x + col * 2,
                symbol,
                curses.color_pair(color_pair),
            )


def draw_legend(stdscr, start_y: int, start_x: int) -> None:
    """Affiche la légende des symboles."""
    _draw_str(stdscr, start_y, start_x, "============= Légende =============", curses.A_BOLD)

    entries_per_line = 3
    column_width = 2  # Largeur de chaque colonne pour espacer les entrées
    
    for i, entry in enumerate(Legend.ENTRIES):
        row = i // entries_per_line  # Calcule le numéro de ligne
        col = i % entries_per_line   # Calcule le numéro de colonne (0, 1 ou 2)
        
        # Position x de la colonne
        x_offset = start_x + col * column_width*7
        
        # Dessine le symbole
        _draw_str(
            stdscr,
            start_y + 1 + row,
            x_offset,
            entry.symbol,
            curses.color_pair(entry.color_pair.value),
        )
        # Dessine le label
        _draw_str(stdscr, start_y + 1 + row, x_offset + 2, entry.label)

def draw_status(
    stdscr,
    start_y: int,
    start_x: int,
    status_info: dict[str, Any],
) -> None:
    """Affiche les informations de status."""
    _draw_str(stdscr, start_y, start_x, "=== Status ===", curses.A_BOLD)

    for i, (key, value) in enumerate(status_info.items()):
        _draw_str(stdscr, start_y + 1 + i, start_x, f"{key}: {value}")

    


def display_simulation(
    hero_positions: list[tuple[int, int]],
    dimension: tuple[int, int],
    grid : list[list[tuple[str,int]]],
    entry_pos: tuple[int, int],
    exit_pos: tuple[int, int],
    status_info: dict[str, Any],
) -> None:
    """Affiche la simulation dans une fenêtre curses.
    Args:
        simulation: Instance de Simulation à afficher.
        
    """

    def _main(stdscr):
        curses.curs_set(0)
        ColorPair.init_curses_colors()
        stdscr.clear()

        rows, cols = dimension

        _draw_str(
            stdscr, self.TITLE_Y, self.TITLE_X, "🏰 DUNGEON MANAGER", curses.A_BOLD
        )

        draw_simulation(
            stdscr,
            hero_positions,
            dimension,
            grid,
            entry_pos,
            exit_pos,
            self.DUNGEON_START_Y,
            self.DUNGEON_START_X,
        )

        draw_legend(stdscr, self.LEGEND_START_Y, self.LEGEND_START_X)
        draw_status(
            stdscr,
            self.STATUS_START_Y,
            self.STATUS_START_X,
            status_info
        )
        
        _draw_str(
            stdscr,
            self.FOOTER_Y,
            self.FOOTER_X,
            "Appuyez sur une touche pour quitter...",
            curses.A_DIM,
        )

        stdscr.refresh()
        stdscr.getch()

    curses.wrapper(_main)


class TUIView:
    """Interface TUI interactive avec gestion des inputs utilisateur."""

    def __init__(self,status_info: dict[str, Any],dimension: tuple[int, int], dungeon_grid : list[list[tuple[str,int]]], entry_pos: tuple[int, int], exit_pos: tuple[int, int],heros_positions: list[tuple[int, int]]) -> None:
        """Initialise la vue TUI."""
        self.running = False
        self.dimension = dimension
        self.status_info: dict[str, Any] = status_info
        self.cursor_pos: tuple[int, int] = (0, 0)
        self.dungeon_grid = dungeon_grid
        self.entry_pos = entry_pos
        self.exit_pos = exit_pos
        self.hero_positions = heros_positions
        
        self.TITLE_Y = 0
        self.TITLE_X = 1
        self.DUNGEON_START_Y = 2
        self.DUNGEON_START_X = 1
        self.LEGEND_START_Y = self.DUNGEON_START_Y + self.dimension[0] + 2
        self.LEGEND_START_X = self.DUNGEON_START_X
        self.STATUS_START_Y = self.DUNGEON_START_Y
        self.STATUS_START_X = self.DUNGEON_START_X + self.dimension[1] * 2 + 3
        self.FOOTER_Y = self.LEGEND_START_Y + 10
        self.FOOTER_X = self.DUNGEON_START_X
        self.HELP_START_Y = self.DUNGEON_START_Y
        self.HELP_START_X = self.STATUS_START_X +23
        
        # # Mapping des touches vers les commandes
        # self.key_bindings: dict[int, Callable[[], None]] = {
        #     ord("q"): self._quit,
        #     ord("s"): self._start_wave,
        #     ord("x"): self._stop_wave,
        #     ord("r"): self._reset_dungeon,
        #     ord("e"): self._export_dungeon,
        #     ord("i"): self._import_dungeon,
        #     curses.KEY_UP: self._move_cursor_up,
        #     curses.KEY_DOWN: self._move_cursor_down,
        #     curses.KEY_LEFT: self._move_cursor_left,
        #     curses.KEY_RIGHT: self._move_cursor_right,
        #     ord("t"): self._place_trap,
        #     ord("w"): self._place_wall,
        #     ord("d"): self._remove_entity,
        # }
    """
    def _quit(self) -> None:
        self.running = False

    def _start_wave(self) -> None:
        commands.startWave(self.game_controller.simulation)

    def _stop_wave(self) -> None:
        self.game_controller.stop()

    def _reset_dungeon(self) -> None:
        self.game_controller.reset_dungeon()

    def _export_dungeon(self) -> None:
        self.game_controller.export_dungeon()

    def _import_dungeon(self) -> None:
        self.game_controller.import_dungeon()
    """

    def _move_cursor(self, delta_row: int, delta_col: int) -> None:
        "Déplace le curseur selon les deltas fournis."
        row, col = self.cursor_pos
        max_row, max_col = self.dimension[0] - 1, self.dimension[1] - 1
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
        
    """
    def _place_trap(self) -> None:
        self.game_controller.place_trap(self.cursor_pos, damage=10)

    def _place_wall(self) -> None:
        self.game_controller.place_wall(self.cursor_pos)

    def _remove_entity(self) -> None:
        self.game_controller.remove_entity(self.cursor_pos)

    """
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
    """
    def update_hero_positions(self) -> None:
        self.hero_positions = self.game_controller.get_hero_positions()
    """
    def update_status_info(self, info: dict[str, Any]) -> None:
        self.status_info = info

    def render(self, stdscr) -> None:
        print("render called")
        stdscr.clear()

        rows, cols = self.dimension

        _draw_str(
            stdscr, self.TITLE_Y, self.TITLE_X, "🏰 DUNGEON MANAGER", curses.A_BOLD
        )

        draw_simulation(
            stdscr,
            self.hero_positions,
            self.dimension,
            self.dungeon_grid,
            self.entry_pos,
            self.exit_pos,
            self.DUNGEON_START_Y,
            self.DUNGEON_START_X,
        )

        self._draw_cursor(stdscr, self.DUNGEON_START_Y, self.DUNGEON_START_X)
        
        draw_legend(stdscr, self.LEGEND_START_Y, self.LEGEND_START_X)

        if self.status_info:
            draw_status(stdscr, self.STATUS_START_Y, self.STATUS_START_X, self.status_info)

        self._draw_help(stdscr, self.HELP_START_Y, self.HELP_START_X)

        _draw_str(
            stdscr,
            self.HELP_START_Y - 1,
            self.HELP_START_X,
            f"Curseur: {self.cursor_pos}",
            curses.A_DIM,
        )
        print("oui")

        stdscr.refresh()
