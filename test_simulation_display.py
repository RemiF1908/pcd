import curses
from src.model.level import LevelBuilder
from src.simulation import Simulation
from src.controller.game_controller import GameController
from src.model.hero import Hero
from src.model.dungeon import Dungeon
from src.model.cell import Cell
from src.model.floor import Floor
from src.view.tui.simulation_display import TUIView, ColorPair

def test_simulation_display_basic(stdscr):
    # Initialisation de curses
    curses.curs_set(0)  # Cache le curseur
    ColorPair.init_curses_colors()  # Initialise les couleurs
    
    gamecontroller = GameController(None, None)
    
    # Création d'un niveau de test
    hero = Hero(pv_total=100, strategy="random")
    hero.awake()
    rows, cols = 10, 10
    dungeon = Dungeon(
        dimension=(rows, cols), 
        grid=[[Cell((r, c), Floor()) for c in range(cols)] for r in range(rows)],
        entry=(0, 0),
        exit=(rows-1, cols-1)
    )
    
    level = (LevelBuilder()
        .set_dungeon(dungeon=dungeon)
        .set_difficulty(4)
        .set_budget(300)
        .add_hero_instance(hero)
        .build())
    
    # Création de la simulation
    simulation = Simulation(level, dungeon)
    gamecontroller.simulation = simulation
    
    view = TUIView(
        status_info=gamecontroller.get_status_info(),
        dimension=gamecontroller.dimension(),
        dungeon_grid=gamecontroller.grid_str(),
        entry_pos=gamecontroller.entry(),
        exit_pos=gamecontroller.exit(),
        heros_positions=gamecontroller.get_hero_positions(),    
    )
    
    # Création du GameController
    gamecontroller.interface = view
    
    # Rendu de l'interface
    view.render(stdscr)
    
    # AJOUT : Attendre une touche pour quitter
    stdscr.refresh()
    stdscr.getch()  # Cette ligne est essentielle pour voir l'affichage

if __name__ == "__main__":
    curses.wrapper(test_simulation_display_basic)