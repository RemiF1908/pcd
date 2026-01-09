from src.view.gui.server import run_server
from src.commands.GameInvoker import GameInvoker
from src.view.input_handler import InputHandler



class GuiView: 
    def __init__(
        self,
        # status_info: dict[str, Any],
        dimension: tuple[int, int],
        entry_pos: tuple[int, int],
        exit_pos: tuple[int, int],
        heros_positions: list[tuple[int, int]],
        invoker: GameInvoker,
        dungeon,
        simulation,
        campaign,
    ) -> None:
        

        self.dimension = dimension
        self.entry_pos = entry_pos
        self.exit_pos = exit_pos
        self.heros_positions = heros_positions
        self.invoker = invoker
        self.dungeon = dungeon
        self.simulation = simulation
        self.campaign = campaign

        self.input_handler = InputHandler(self.simulation, self.dungeon, self.invoker, self.campaign)
    



    def run(self) -> None:
        run_server(self.dungeon, self.input_handler, self.simulation)