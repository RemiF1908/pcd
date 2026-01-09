import argparse
from src.model.level import LevelBuilder
from src.simulation import Simulation
from src.controller.game_controller import GameController
from src.model.hero import Hero
from src.model.dungeon import Dungeon
from src.model.cell import Cell
from src.model.floor import Floor
from src.model.wall import Wall
from src.model.trap import Trap
from src.model.campaign_manager import Campaign
from src.view.tui.simulation_display import TUIView, ColorPair
from src.view.gui.gui import GuiView
from src.commands.GameInvoker import GameInvoker

def main():
    parser = argparse.ArgumentParser(description="Dungeon Manager")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--tui", action="store_true", help="Run the terminal interface")
    group.add_argument("--web", action="store_true", help="Run the web interface")
    args = parser.parse_args()
    print(args)

    campaign = Campaign()
    current_level = campaign.load_level(1)
    if not current_level:
        print("Error: Could not load the first level.")
        return

    simulation = Simulation(current_level, current_level.dungeon)
    gamecontroller = GameController(None, simulation, campaign)
    invoker = GameInvoker(gamecontroller)

    if args.tui:
        view = TUIView(
            status_info=gamecontroller.get_status_info(),
            dimension=gamecontroller.dimension(),
            entry_pos=gamecontroller.entry(),
            exit_pos=gamecontroller.exit(),
            heros_positions=gamecontroller.get_hero_positions(),
            invoker=invoker,
            dungeon=gamecontroller.dungeon,
            simulation=gamecontroller.simulation,
            campaign=campaign,
        )

    elif args.web:
        view = GuiView(
            dimension=gamecontroller.dimension(),
            entry_pos=gamecontroller.entry(),
            exit_pos=gamecontroller.exit(),
            heros_positions=gamecontroller.get_hero_positions(),
            invoker=invoker,
            dungeon=gamecontroller.dungeon,
            simulation=gamecontroller.simulation,
            campaign=campaign,
        )

    gamecontroller.interface = view

    view.run()


if __name__ == "__main__":
    main()
