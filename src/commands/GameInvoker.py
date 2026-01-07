class GameInvoker:
    def __init__(self, game_controller):
        self.history = []
        self.commandstack = []
        self.game_controller = game_controller

    def execute(self):
        for command in self.commandstack:
            command.execute(self.game_controller)
            self.history.append(command)
        self.commandstack = []

    def push_command(self, command):
        self.commandstack.append(command)
