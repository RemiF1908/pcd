class GameInvoker:
    def __init__(self):
        self.history = []
        self.commandstack = []

    def execute(self) :
        for command in self.commandstack :
            command.execute()
            self.history.append(command)
        self.commandstack = []
    
    def push_command(self, command):
        self.commandstack.append(command)
