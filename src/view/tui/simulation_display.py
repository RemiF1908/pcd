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
from src.commands import *
from src.commands.GameInvoker import GameInvoker
from src.commands.startWave import startWave
from src.commands.stopWave import stopWave
from src.commands.resetDungeon import resetDungeon
from src.commands.placeEntity import placeEntity
from src.commands.removeEntity import removeEntity
from src.commands.exportDungeon import exportDungeon
from src.commands.importDungeon import importDungeon
from src.model.entity_factory import EntityFactory
from src.view.tui.input_handler import InputHandler


class ColorPair(Enum):
    """Paires de couleurs pour curses."""

    FLOOR = 1
    WALL = 2
    TRAP = 3
    DRAGON = 4
    ENTRANCE = 5
    EXIT = 6
    HERO = 7
    BOMBE = 8

    @classmethod
    def init_curses_colors(cls) -> None:
        """Initialise les paires de couleurs curses."""
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(cls.FLOOR.value, curses.COLOR_WHITE, -1)
        curses.init_pair(cls.WALL.value, curses.COLOR_WHITE, -1)
        curses.init_pair(cls.TRAP.value, curses.COLOR_RED, -1)
        curses.init_pair(cls.DRAGON.value, curses.COLOR_MAGENTA, -1)
        curses.init_pair(cls.ENTRANCE.value, curses.COLOR_GREEN, -1)
        curses.init_pair(cls.EXIT.value, curses.COLOR_CYAN, -1)
        curses.init_pair(cls.HERO.value, curses.COLOR_YELLOW, -1)
        curses.init_pair(cls.BOMBE.value, curses.COLOR_RED, -1)

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
        LegendEntry("Z", "Dragon", ColorPair.DRAGON),
        LegendEntry("E", "Entrance", ColorPair.ENTRANCE),
        LegendEntry("S", "Exit", ColorPair.EXIT),
        LegendEntry("H", "Hero", ColorPair.HERO),
        LegendEntry("B", "Bombe", ColorPair.BOMBE),
    ]

    @classmethod
    def get_symbol_for(cls, entity_type: str) -> str:
        """Retourne le symbole pour un type d'entité."""
        for entry in cls.ENTRIES:
            if entry.label.upper() == entity_type:
                return entry.symbol
        return "+"


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
    # Paire 8 : Bombe (rouge)
    curses.init_pair(8, curses.COLOR_RED, -1)


def _get_cell_display(
    dungeon, pos: tuple[int, int], hero_set: set[tuple[int, int]]
) -> tuple[str, int]:
    """Détermine le symbole et la couleur pour une cellule."""
    if pos in hero_set:
        return "H", ColorPair.MONSTER.value
    if pos == dungeon.entry:
        return Legend.get_symbol_for("ENTRANCE"), ColorPair.ENTRANCE.value
    if pos == dungeon.exit:
        return Legend.get_symbol_for("EXIT"), ColorPair.EXIT.value

    cell = dungeon.get_cell(pos)
    if cell.entity is not None:
        return cell.entity.get_display_char(), cell.entity.get_color_id()

    return "+", 0


def draw_simulation(
    stdscr,
    hero_positions: list[tuple[int, int]],
    dimension: tuple[int, int],
    dungeon,
    entry_pos: tuple[int, int],
    exit_pos: tuple[int, int],
    start_y: int = 1,
    start_x: int = 1,
) -> None:
    """Dessine le donjon sur la fenêtre curses.

    Args:
        stdscr: Fenêtre curses standard.
        hero_positions: Positions des héros.
        dimension: Dimensions du donjon.
        dungeon: Objet Dungeon à afficher.
        entry_pos: Position d'entrée.
        exit_pos: Position de sortie.
        start_y: Ligne de départ pour l'affichage.
        start_x: Colonne de départ pour l'affichage.
    """

    rows, cols = dimension
    hero_set = set(hero_positions) if hero_positions else set()

    grid_str = []
    for row in dungeon.grid:
        str_row = []
        for cell in row:
            if cell.entity is not None:
                str_row.append(
                    (cell.entity.get_display_char(), cell.entity.get_color_id())
                )
            else:
                str_row.append(("+", 0))
        grid_str.append(str_row)

    for row in range(rows):
        for col in range(cols):
            pos = (row, col)
            symbol, color_pair = grid_str[row][col]
            if pos in hero_set:
                symbol, color_pair = Legend.get_symbol_for("HERO"), ColorPair.HERO.value
            elif pos == entry_pos:
                symbol, color_pair = (
                    Legend.get_symbol_for("ENTRANCE"),
                    ColorPair.ENTRANCE.value,
                )
            elif pos == exit_pos:
                symbol, color_pair = Legend.get_symbol_for("EXIT"), ColorPair.EXIT.value
            _draw_str(
                stdscr,
                start_y + row,
                start_x + col * 2,
                symbol,
                curses.color_pair(color_pair),
            )


def draw_dungeon(
    stdscr,
    dungeon,
    start_y: int = 1,
    start_x: int = 1,
    hero_positions: list[tuple[int, int]] | None = None,
) -> None:
    """Dessine le donjon sur la fenêtre curses (wrapper pour compatibilité avec les tests).

    Args:
        stdscr: Fenêtre curses standard.
        dungeon: Instance de Dungeon à afficher.
        start_y: Ligne de départ pour l'affichage.
        start_x: Colonne de départ pour l'affichage.
        hero_positions: Liste des positions des héros.
    """
    if hero_positions is None:
        hero_positions = []

    grid_str = []
    for row in dungeon.grid:
        str_row = []
        for cell in row:
            if cell.entity is not None:
                str_row.append(
                    (cell.entity.get_display_char(), cell.entity.get_color_id())
                )
            else:
                str_row.append(("+", 0))
        grid_str.append(str_row)

    draw_simulation(
        stdscr,
        hero_positions,
        dungeon.dimension,
        grid_str,
        dungeon.entry,
        dungeon.exit,
        start_y,
        start_x,
    )


def display_dungeon(
    dungeon,
    hero_positions: list[tuple[int, int]] | None = None,
    status_info: dict[str, Any] | None = None,
) -> None:
    """Affiche le donjon dans une fenêtre curses (wrapper pour compatibilité avec les tests).

    Args:
        dungeon: Instance de Dungeon à afficher.
        hero_positions: Liste des positions des héros.
        status_info: Informations de statut à afficher.
    """
    if hero_positions is None:
        hero_positions = []

    if status_info is None:
        status_info = {}

    grid_str = []
    for row in dungeon.grid:
        str_row = []
        for cell in row:
            if cell.entity is not None:
                str_row.append(
                    (cell.entity.get_display_char(), cell.entity.get_color_id())
                )
            else:
                str_row.append(("+", 0))
        grid_str.append(str_row)

    display_simulation(
        hero_positions,
        dungeon.dimension,
        grid_str,
        dungeon.entry,
        dungeon.exit,
        status_info,
    )


def draw_legend(stdscr, start_y: int, start_x: int) -> None:
    """Affiche la légende des symboles."""
    _draw_str(stdscr, start_y, start_x, "=== Légende ===", curses.A_BOLD)

    entries_per_line = 3
    column_width = 2  # Largeur de chaque colonne pour espacer les entrées
    
    for i, entry in enumerate(Legend.ENTRIES):
        row = i // entries_per_line  # Calcule le numéro de ligne
        col = i % entries_per_line   # Calcule le numéro de colonne (0, 1 ou 2)
        
        # Position x de la colonne
        x_offset = start_x + col * column_width * 7
        
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
    grid: list[list[tuple[str, int]]],
    entry_pos: tuple[int, int],
    exit_pos: tuple[int, int],
    status_info: dict[str, Any],
) -> None:
    """Affiche la simulation dans une fenêtre curses.
    Args:
        hero_positions: Positions des héros.
        dimension: Dimensions du donjon.
        grid: Grille du donjon.
        entry_pos: Position d'entrée.
        exit_pos: Position de sortie.
        status_info: Informations de statut.
    """
    TITLE_Y = 0
    TITLE_X = 1
    DUNGEON_START_Y = 2
    DUNGEON_START_X = 1
    LEGEND_START_Y = DUNGEON_START_Y + dimension[0] + 2
    LEGEND_START_X = DUNGEON_START_X
    STATUS_START_Y = DUNGEON_START_Y
    STATUS_START_X = DUNGEON_START_X + dimension[1] * 2 + 3
    FOOTER_Y = LEGEND_START_Y + 10
    FOOTER_X = DUNGEON_START_X

    def _main(stdscr):
        curses.curs_set(0)
        ColorPair.init_curses_colors()
        stdscr.clear()

        rows, cols = dimension

        _draw_str(stdscr, TITLE_Y, TITLE_X, "🏰 DUNGEON MANAGER", curses.A_BOLD)

        draw_simulation(
            stdscr,
            hero_positions,
            dimension,
            grid,
            entry_pos,
            exit_pos,
            DUNGEON_START_Y,
            DUNGEON_START_X,
        )

        draw_legend(stdscr, LEGEND_START_Y, LEGEND_START_X)
        draw_status(stdscr, STATUS_START_Y, STATUS_START_X, status_info)

        _draw_str(
            stdscr,
            FOOTER_Y,
            FOOTER_X,
            "Appuyez sur une touche pour quitter...",
            curses.A_DIM,
        )

        stdscr.refresh()
        stdscr.getch()

    curses.wrapper(_main)


def draw_log(
    stdscr,
    start_y: int,
    start_x: int,
    log: str,
) -> None:
    """Affiche les informations de status."""
    _draw_str(stdscr, start_y, start_x, "=== Log ===", curses.A_BOLD)

    _draw_str(stdscr, start_y + 1, start_x, f"{log}")


class TUIView:
    """Interface TUI interactive avec gestion des inputs utilisateur."""

    def __init__(
        self,
        status_info: dict[str, Any],
        dimension: tuple[int, int],
        entry_pos: tuple[int, int],
        exit_pos: tuple[int, int],
        heros_positions: list[tuple[int, int]],
        invoker: GameInvoker,
        dungeon,
        simulation,
    ) -> None:
        """Initialise la vue TUI."""

        self.dungeon = dungeon
        self.running = False
        self.dimension = self.dungeon.dimension
        self.status_info = status_info
        self.cursor_pos: tuple[int, int] = (0, 0)
        self.entry_pos = entry_pos
        self.exit_pos = exit_pos
        self.hero_positions = heros_positions
        self.dungeon = dungeon
        self.simulation = simulation
        self.log = ""

        self.TITLE_Y = 0
        self.TITLE_X = 1
        self.DUNGEON_START_Y = 2
        self.DUNGEON_START_X = 1
        self.LEGEND_START_Y = self.DUNGEON_START_Y + self.dimension[0] + 2
        self.LEGEND_START_X = self.DUNGEON_START_X
        self.LEGEND_X = self.DUNGEON_START_X
        self.STATUS_START_Y = self.DUNGEON_START_Y
        self.STATUS_START_X = self.DUNGEON_START_X + self.dimension[1] * 2 + 3
        self.LOG_START_Y = self.DUNGEON_START_Y 
        self.LOG_START_X = self.DUNGEON_START_X + self.dimension[1] * 8 
        self.FOOTER_Y = self.LEGEND_START_Y + 10
        self.FOOTER_X = self.DUNGEON_START_X
        self.HELP_START_Y = self.DUNGEON_START_Y
        self.HELP_START_X = self.STATUS_START_X + 23

        self.invoker = invoker
        self.input_handler = InputHandler(self, self.invoker)

        # Mapping des touches vers les commandes
        self.key_bindings: dict[int, Callable[[], None]] = {
            ord("q"): self.input_handler.quit,
            ord("s"): self.input_handler.start_wave,
            ord("x"): self.input_handler.stop_wave,
            ord("r"): self.input_handler.reset_dungeon,
            ord("e"): self.input_handler.export_dungeon,
            ord("i"): self.input_handler.import_dungeon,
            curses.KEY_UP: self.input_handler.move_cursor_up,
            curses.KEY_DOWN: self.input_handler.move_cursor_down,
            curses.KEY_LEFT: self.input_handler.move_cursor_left,
            curses.KEY_RIGHT: self.input_handler.move_cursor_right,
            ord("t"): self.input_handler.place_trap,
            ord("w"): self.input_handler.place_wall,
            ord("z"): self.input_handler.place_dragon,
            ord("b"): self.input_handler.place_bombe,
            ord("d"): self.input_handler.remove_entity,
        }

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
            ("z: Dragon", 0),
            ("b: Bombe", 0),
            ("d: Delete (supprimer)", 0),
        ]

        for i, (text, attr) in enumerate(help_text):
            _draw_str(stdscr, start_y + i, start_x, text, attr)

    def update_hero_positions(self, positions: list[tuple[int, int]]) -> None:
        self.hero_positions = positions

    def update_status_info(self, info: dict[str, Any]) -> None:
        self.status_info = info

    def update_hero_positions_from_simulation(self) -> None:
        """Met à jour les positions des héros et les infos de statut depuis la simulation."""
        if self.simulation and hasattr(self.simulation, "level"):
            # Utilise get_all_hero_positions pour afficher tous les héros, même non réveillés
            self.hero_positions = self.simulation.get_all_hero_positions()
            # Met à jour aussi les infos de statut
            if (
                self.invoker
                and hasattr(self.invoker, "game_controller")
                and self.invoker.game_controller
            ):
                self.status_info = self.invoker.game_controller.get_status_info()

    def render(self, stdscr) -> None:
        stdscr.clear()

        rows, cols = self.dimension

        _draw_str(
            stdscr, self.TITLE_Y, self.TITLE_X, "🏰 DUNGEON MANAGER", curses.A_BOLD
        )

        draw_simulation(
            stdscr,
            self.hero_positions,
            self.dimension,
            self.dungeon,
            self.entry_pos,
            self.exit_pos,
            self.DUNGEON_START_Y,
            self.DUNGEON_START_X,
        )

        self._draw_cursor(stdscr, self.DUNGEON_START_Y, self.DUNGEON_START_X)

        draw_legend(stdscr, self.LEGEND_START_Y, self.LEGEND_START_X)

        if self.status_info:
            draw_status(
                stdscr, self.STATUS_START_Y, self.STATUS_START_X, self.status_info
            )

        draw_log(stdscr, self.LOG_START_Y, self.LOG_START_X, self.log)

        self._draw_help(stdscr, self.HELP_START_Y, self.HELP_START_X)

        _draw_str(
            stdscr,
            self.HELP_START_Y - 1,
            self.HELP_START_X,
            f"Curseur: {self.cursor_pos}",
            curses.A_DIM,
        )

        stdscr.refresh()

    def run(self) -> None:
        """Lance la boucle principale de la TUI."""

        def _main(stdscr):
            curses.curs_set(0)  # Cache le curseur
            ColorPair.init_curses_colors()  # Initialise les couleurs
            stdscr.nodelay(True)
            stdscr.timeout(100)
            self.running = True
            while self.running:
                # Met à jour les positions des héros depuis la simulation
                self.update_hero_positions_from_simulation()
                if self.simulation.heroes and hasattr(
                    self.simulation.heroes[0], "path"
                ):
                    self.log = [h.ticktoAwake for h in self.simulation.heroes].__str__()
                self.render(stdscr)
                key = stdscr.getch()
                if key in self.key_bindings:
                    self.key_bindings[key]()

        curses.wrapper(_main)
