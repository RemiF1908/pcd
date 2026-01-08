from src.model.level import LevelBuilder
from src.simulation import Simulation
from src.controller.game_controller import GameController
from src.model.hero import Hero
from src.model.dungeon import Dungeon
from src.model.cell import Cell
from src.model.floor import Floor
from src.model.wall import Wall
from src.model.wall_creator import WallCreator
from src.model.bombe_creator import BombeCreator
from src.model.dragon_creator import DragonCreator
from src.model.trap_creator import TrapCreator
from src.model.trap import Trap
from src.model.dragon import Dragon
from src.view.tui.simulation_display import TUIView, ColorPair
from src.view.gui.gui import GuiView

from src.commands.GameInvoker import GameInvoker


def test_simulation_display_basic():
    gamecontroller = GameController(None, None)
    invoker = GameInvoker(gamecontroller)

    # Création d'un niveau de test
    hero = Hero(pv_total=100, strategy="shortest")
    rows, cols = 5,5
    dungeon = Dungeon(
        dimension=(rows, cols),
        grid=[[Cell((r, c), Floor()) for c in range(cols)] for r in range(rows)],
        entry=(0, 0),
        exit=(rows - 1, cols - 1),
    )
    # 2. Ajout d'obstacles (Le L de murs)
    walls = [(2,0),(2,3)]
    for r, c in walls:
        dungeon.place_entity(WallCreator().build(), (r, c))
    
    # 3. Ajout de pièges (sur le chemin direct)
    traps = [(2,1),(2,2),(3,2)]
    for r, c in traps:
        dungeon.place_entity(TrapCreator().build(), (r, c))
    
    # 4. Ajout d'une bombe et d'un dragon
    dungeon.place_entity(BombeCreator().build(), (0, 1))
    dungeon.place_entity(Dragon('R'), (3, 4))

    level = (
        LevelBuilder()
        .set_dungeon(dungeon=dungeon)
        .set_difficulty(4)
        .set_budget(300)
        .add_hero_instance(hero)
        .build()
    )

    # Création de la simulation
    simulation = Simulation(level, dungeon)
    gamecontroller.simulation = simulation

    view = GuiView(
        dimension=gamecontroller.dimension(),
        entry_pos=gamecontroller.entry(),
        exit_pos=gamecontroller.exit(),
        heros_positions=gamecontroller.get_hero_positions(),
        invoker=invoker,
        dungeon=gamecontroller.dungeon,
        simulation=gamecontroller.simulation,
    )

    # Création du GameController
    gamecontroller.interface = view

    view.run()


if __name__ == "__main__":
    test_simulation_display_basic()
