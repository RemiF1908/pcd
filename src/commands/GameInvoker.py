from src.commands import startWave


class GameInvoker:
    def __init__(self, game_controller):
        self.history = []
        self.commandstack = []
        self.game_controller = game_controller

    def execute(self):
        result = None
        for command in self.commandstack:
            res = command.execute(self.game_controller)
            if isinstance(command, startWave):
                result = res
            self.history.append(command)
        self.commandstack = []
        if self.game_controller and self.game_controller.simulation:
            self.game_controller.simulation.notify()
        return result

    def push_command(self, command):
        self.commandstack.append(command)
