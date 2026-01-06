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

import curses
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.model.dungeon import Dungeon


# Couleurs spéciales pour les entités sans méthode get_color_id
SPECIAL_COLORS = {
    "ENTRANCE": 5,   # Vert
    "EXIT": 6,       # Cyan
    "HERO": 7,       # Jaune
}

# Symboles spéciaux
SPECIAL_SYMBOLS = {
    "ENTRANCE": "E",
    "EXIT": "S",
    "HERO": "@",
}


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
            cell = dungeon.get_cell((row, col))
            pos = (row, col)

            # Déterminer le symbole et la couleur via polymorphisme
            if pos in hero_set:
                symbol = SPECIAL_SYMBOLS["HERO"]
                color_pair = SPECIAL_COLORS["HERO"]
            elif pos == dungeon.entry:
                symbol = SPECIAL_SYMBOLS["ENTRANCE"]
                color_pair = SPECIAL_COLORS["ENTRANCE"]
            elif pos == dungeon.exit:
                symbol = SPECIAL_SYMBOLS["EXIT"]
                color_pair = SPECIAL_COLORS["EXIT"]
            elif cell.entity is not None:
                # Utiliser les méthodes polymorphiques de l'entité
                symbol = cell.entity.get_display_char()
                color_pair = cell.entity.get_color_id()
            else:
                # Case vide par défaut
                symbol = "."
                color_pair = 0

            # Dessiner le caractère
            try:
                stdscr.addch(start_y + row, start_x + col * 2, symbol, curses.color_pair(color_pair))
            except curses.error:
                # Ignore les erreurs si on dépasse la fenêtre
                pass


def draw_legend(stdscr, start_y: int, start_x: int) -> None:
    """Affiche la légende des symboles."""
    legend = [
        (". ", "Floor", 1),
        ("# ", "Wall", 2),
        ("^ ", "Trap", 3),
        ("M ", "Monster", 4),
        ("E ", "Entrance", 5),
        ("S ", "Exit", 6),
        ("@ ", "Hero", 7),
    ]

    stdscr.addstr(start_y, start_x, "=== Légende ===", curses.A_BOLD)
    for i, (sym, label, color) in enumerate(legend):
        try:
            stdscr.addstr(start_y + 1 + i, start_x, sym, curses.color_pair(color))
            stdscr.addstr(label)
        except curses.error:
            pass


def draw_status(stdscr, start_y: int, start_x: int, info: dict) -> None:
    """Affiche des informations de status (tour, héros restants, etc.).

    Args:
        stdscr: Fenêtre curses.
        start_y, start_x: Position.
        info: Dictionnaire avec les infos à afficher.
              Ex: {"turn": 5, "heroes_alive": 2, "budget": 100}
    """
    stdscr.addstr(start_y, start_x, "=== Status ===", curses.A_BOLD)
    line = 1
    for key, value in info.items():
        try:
            stdscr.addstr(start_y + line, start_x, f"{key}: {value}")
            line += 1
        except curses.error:
            pass


def display_dungeon(
    dungeon: "Dungeon",
    hero_positions: list[tuple[int, int]] | None = None,
    status_info: dict | None = None,
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
        curses.curs_set(0)  # Cacher le curseur
        _init_colors()
        stdscr.clear()

        rows, cols = dungeon.dimension

        # Titre
        stdscr.addstr(0, 1, "🏰 DUNGEON MANAGER", curses.A_BOLD)

        # Dessiner le donjon
        draw_dungeon(stdscr, dungeon, start_y=2, start_x=1, hero_positions=hero_positions)

        # Légende à droite du donjon
        legend_x = 2 + cols * 2 + 3
        draw_legend(stdscr, start_y=2, start_x=legend_x)

        # Status en dessous de la légende
        if status_info:
            draw_status(stdscr, start_y=12, start_x=legend_x, info=status_info)

        # Instructions en bas
        footer_y = max(rows + 4, 20)
        stdscr.addstr(footer_y, 1, "Appuyez sur une touche pour quitter...", curses.A_DIM)

        stdscr.refresh()
        stdscr.getch()  # Attendre une touche

    curses.wrapper(_main)


# === Démo rapide si exécuté directement ===
if __name__ == "__main__":
    # Démo avec un petit donjon de test
    from src.model.dungeon import Dungeon
    from src.model.cell import Cell
    from src.model.entity_factory import EntityFactory

    # Créer une grille 8x10
    rows, cols = 8, 10
    grid = [[Cell((r, c), EntityFactory.create_floor()) for c in range(cols)] for r in range(rows)]

    # Placer quelques murs
    for c in range(2, 8):
        grid[2][c].entity = EntityFactory.create_wall()
    for r in range(2, 6):
        grid[r][7].entity = EntityFactory.create_wall()

    # Placer des pièges
    grid[4][3].entity = EntityFactory.create_trap(damage=10)
    grid[5][5].entity = EntityFactory.create_trap(damage=15)

    # Créer le donjon
    dungeon = Dungeon(
        dimension=(rows, cols),
        grid=grid,
        entry=(0, 0),
        exit=(rows - 1, cols - 1),
    )

    # Afficher avec des héros
    hero_positions = [(0, 0), (1, 1)]
    status_info = {"Tour": 1, "Héros vivants": 2, "Budget": 100}

    display_dungeon(dungeon, hero_positions=hero_positions, status_info=status_info)
