from src.model.level import LevelBuilder
from src.simulation import Simulation
from src.controller.game_controller import GameController
from src.model.hero import Hero
from src.model.dungeon import Dungeon
from src.model.cell import Cell
from src.model.floor import Floor
from src.model.wall import Wall
from src.model.trap import Trap
from src.view.tui.simulation_display import TUIView, ColorPair
from src.commands.GameInvoker import GameInvoker


def test_simulation_display_basic():
    gamecontroller = GameController(None, None)
    invoker = GameInvoker(gamecontroller)

    # Création d'un niveau de test
    hero = Hero(pv_total=100, strategy="shortest")
    rows, cols = 10, 10
    dungeon = Dungeon(
        dimension=(rows, cols),
        grid=[[Cell((r, c), Floor()) for c in range(cols)] for r in range(rows)],
        entry=(0, 0),
        exit=(rows - 1, cols - 1),
    )

    level = (
        LevelBuilder()
        .set_dungeon(dungeon=dungeon)
        .set_difficulty(4)
        .set_budget(300)
        .add_hero_instance(hero)
        .build()
    )

    # Création de la simulation
    simulation = Simulation(level, level.dungeon)
    gamecontroller.simulation = simulation

    view = TUIView(
        status_info=gamecontroller.get_status_info(),
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
